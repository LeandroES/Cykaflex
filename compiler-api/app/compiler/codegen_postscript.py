"""
Cykaflex PostScript Code Generator
====================================
**Visitor pattern** implementation that traverses a Cykaflex AST and emits
valid PostScript (PS-Adobe-3.0) source suitable for ``.ps`` files.

Architecture
------------
``LayoutEngine``
    Stateful helper that tracks the cursor position (x, y), handles
    word-wrapping, font switching, and automatic page breaks.

``PostScriptVisitor``
    Concrete :class:`~.ast_nodes.NodeVisitor`.  Each ``visit_*`` method
    calls the appropriate ``LayoutEngine`` operation.

``generate()``
    Public convenience function — parse + visit in one call.

PostScript layout constants
---------------------------
* Page format : A4 (595 × 842 pt)
* Margins     : 72 pt (1 in) on every side
* Content area: 451 × 698 pt
* Fonts       : standard Type-1 Helvetica family (guaranteed in all PS viewers)

Example output fragment::

    %!PS-Adobe-3.0
    %%Title: Mi Documento
    %%Creator: Cykaflex Compiler 0.1
    %%Pages: (atend)
    %%BoundingBox: 0 0 595 842
    %%EndComments
    ...
    %%Page: 1 1
    /Helvetica-Bold findfont 20 scalefont setfont
    297 740 moveto (La Ciencia de Cykaflex) show
    ...
    showpage
    %%Trailer
    %%Pages: 2
    %%EOF
"""

from __future__ import annotations

import textwrap
from datetime import datetime, timezone

from .ast_nodes import (
    ChapterNode,
    DocumentNode,
    ListItemNode,
    ListNode,
    NewPageNode,
    NodeVisitor,
    SectionNode,
    SubSectionNode,
    SubSubSectionNode,
    TextNode,
    TitlePageNode,
)

# ---------------------------------------------------------------------------
# Page geometry & font constants
# ---------------------------------------------------------------------------

_PAGE_W    = 595   # A4 width  in points
_PAGE_H    = 842   # A4 height in points
_MARGIN_X  = 72    # Left / right margin (1 inch)
_MARGIN_Y  = 72    # Top  / bottom margin (1 inch)
_CONTENT_W = _PAGE_W - 2 * _MARGIN_X   # 451 pt usable width

# Standard PostScript Type-1 font names (available in every PS interpreter)
_FONT_NORMAL      = "Helvetica-Latin1"
_FONT_BOLD        = "Helvetica-Bold-Latin1"
_FONT_ITALIC      = "Helvetica-Oblique-Latin1"
_FONT_BOLD_ITALIC = "Helvetica-BoldOblique-Latin1"

# Average character-width coefficient for Helvetica (empirical)
_CHAR_W = 0.55

# Vertical space added before/after structural elements (points)
_SPACE_BEFORE_HEADING = 14
_SPACE_AFTER_HEADING  = 6
_SPACE_BEFORE_TEXT    = 4
_SPACE_AFTER_TEXT     = 4
_SPACE_LIST           = 4


# ---------------------------------------------------------------------------
# Layout engine
# ---------------------------------------------------------------------------

class LayoutEngine:
    """Maintains cursor state and translates drawing operations to PS commands.

    Parameters
    ----------
    base_font_size:
        The document's base body-text size in points.

    Attributes
    ----------
    lines:
        Accumulated PostScript command strings (one logical command per entry).
    page:
        Current page number (1-indexed; 0 before the first page is opened).
    """

    def __init__(self, base_font_size: int = 12) -> None:
        self.lines:  list[str] = []
        self.page:   int = 0
        self._base   = base_font_size
        self._x      = _MARGIN_X
        self._y      = _PAGE_H - _MARGIN_Y
        self._font   = _FONT_NORMAL
        self._size   = base_font_size
        self._start_page()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _emit(self, cmd: str) -> None:
        self.lines.append(cmd)

    @staticmethod
    def _escape(text: str) -> str:
        """Escape characters special inside PostScript string literals ( ) and handle Latin-1."""
        encoded = text.encode('latin-1', errors='replace')
        res = []
        for b in encoded:
            if b in (92, 40, 41):  # '\', '(', ')'
                res.append('\\' + chr(b))
            elif 32 <= b <= 126:
                res.append(chr(b))
            else:
                # Convert non-ASCII characters (like ñ, á) to PostScript octal sequences
                res.append(f"\\{b:03o}")
        return "".join(res)

    def _chars_per_line(self, size: int, indent_pts: int = 0) -> int:
        """Estimate maximum characters that fit in one line of *size* pt text."""
        usable = _CONTENT_W - indent_pts
        return max(10, int(usable / (size * _CHAR_W)))

    def _line_h(self, size: int) -> int:
        """Return the vertical step (baseline-to-baseline) for *size* pt text."""
        return round(size * 1.4)

    def _set_font(self, name: str, size: int) -> None:
        """Emit a PS font command only when the font or size actually changes."""
        if name != self._font or size != self._size:
            self._emit(f"/{name} findfont {size} scalefont setfont")
            self._font = name
            self._size = size

    def _check_break(self, needed_pts: int) -> None:
        """Force a page break when *needed_pts* would exceed the bottom margin."""
        if self._y - needed_pts < _MARGIN_Y:
            self._end_page()
            self._start_page()

    def _start_page(self) -> None:
        self.page += 1
        self._emit(f"%%Page: {self.page} {self.page}")
        self._x = _MARGIN_X
        self._y = _PAGE_H - _MARGIN_Y
        # Reissue font declaration on every new page (PS state is reset)
        self._emit(f"/{self._font} findfont {self._size} scalefont setfont")

    def _end_page(self) -> None:
        self._emit("showpage")

    def _draw_line(self, text: str, x_override: int | None = None) -> None:
        """Move to the current cursor position and ``show`` *text*."""
        lh = self._line_h(self._size)
        self._check_break(lh)
        x = x_override if x_override is not None else self._x
        self._emit(f"{x} {self._y} moveto ({self._escape(text)}) show")
        self._y -= lh

    def _wrap_draw(
        self,
        text: str,
        font: str,
        size: int,
        indent_pts: int = 0,
        x_center: bool = False,
        justify: bool = False,
    ) -> None:
        """Set font, word-wrap *text*, and draw each wrapped line."""
        self._set_font(font, size)
        width = self._chars_per_line(size, indent_pts)
        wrapped = textwrap.wrap(text, width=width) or [""]
        last_idx = len(wrapped) - 1

        for idx, line in enumerate(wrapped):
            if x_center:
                str_w = len(line) * size * _CHAR_W
                cx = max(_MARGIN_X, int((_PAGE_W - str_w) / 2))
                self._draw_line(line, x_override=cx)
            elif justify and idx < last_idx:
                # --- AQUÍ ESTÁ LA MAGIA ---
                # Le pasamos a la macro JustifyShow el texto y el ancho objetivo exacto.
                # PostScript calculará milimétricamente cuánto espacio inyectar.
                target_w = _CONTENT_W - indent_pts
                lh = self._line_h(self._size)
                self._check_break(lh)
                x = self._x + indent_pts
                self._emit(f"{x} {self._y} moveto ({self._escape(line)}) {target_w} JustifyShow")
                self._y -= lh
            else:
                old_x = self._x
                self._x += indent_pts
                self._draw_line(line)
                self._x = old_x

    # ------------------------------------------------------------------
    # Public drawing operations (called by the visitor)
    # ------------------------------------------------------------------

    def vspace(self, pts: int) -> None:
        """Advance the cursor downward by *pts* points (no ink)."""
        self._y -= pts
        if self._y < _MARGIN_Y:
            self._end_page()
            self._start_page()

    def draw_title(self, text: str, style: str, base_size: int) -> None:
        """Render a document title — centred, large, bold or italic.

        Parameters
        ----------
        text:
            Title string.
        style:
            ``'negrita'`` → Helvetica-Bold; ``'cursiva'`` → Helvetica-Oblique.
        base_size:
            Document base font size; title is rendered at ``base_size + 8``.
        """
        size = base_size + 8
        font = _FONT_BOLD if style == "negrita" else _FONT_ITALIC
        self.vspace(_SPACE_BEFORE_HEADING * 2)
        self._wrap_draw(text, font, size, x_center=True)
        self.vspace(_SPACE_AFTER_HEADING * 2)

    def draw_heading(self, text: str, level: int, base_size: int) -> None:
        """Render a structural heading (chapter / section / subsection / …).

        Parameters
        ----------
        level:
            1 = chapter, 2 = section, 3 = subsection, 4 = subsubsection.
        base_size:
            Document base font size.
        """
        size_delta = {1: 8, 2: 4, 3: 2, 4: 1}
        size = base_size + size_delta.get(level, 0)

        self.vspace(_SPACE_BEFORE_HEADING)
        self._wrap_draw(text, _FONT_BOLD, size)

        # Decorative horizontal rule for chapter and section headings
        if level <= 2:
            rule_y = self._y + self._line_h(size) // 4
            self._emit(
                f"newpath {_MARGIN_X} {rule_y} moveto "
                f"{_MARGIN_X + _CONTENT_W} {rule_y} lineto stroke"
            )
            self._y -= 2

        self.vspace(_SPACE_AFTER_HEADING)

    def draw_text(
        self,
        text: str,
        size: int,
        is_bold: bool = False,
        is_italic: bool = False,
    ) -> None:
        """Render a paragraph of body text with word-wrapping and full justification.

        Parameters
        ----------
        size:
            Font size in points (document base or per-paragraph override).
        is_bold:
            Render in bold weight.
        is_italic:
            Render in italic (oblique) style.
        """
        if is_bold and is_italic:
            font = _FONT_BOLD_ITALIC
        elif is_bold:
            font = _FONT_BOLD
        elif is_italic:
            font = _FONT_ITALIC
        else:
            font = _FONT_NORMAL

        self.vspace(_SPACE_BEFORE_TEXT)
        self._wrap_draw(text, font, size, justify=True)
        self.vspace(_SPACE_AFTER_TEXT)

    def draw_list(self, items: list[str], ordered: bool, base_size: int) -> None:
        """Render an ordered or unordered list.

        Parameters
        ----------
        items:
            Plain-text content of each list item.
        ordered:
            ``True`` → numbered (1. 2. …); ``False`` → bulleted (- …).
        base_size:
            Document base font size.
        """
        self.vspace(_SPACE_LIST)
        self._set_font(_FONT_NORMAL, base_size)

        for idx, item_text in enumerate(items, start=1):
            marker = f"{idx}." if ordered else "-"
            prefix = f"  {marker} "
            indent_pts = round(len(prefix) * base_size * _CHAR_W)

            # Word-wrap the item content, accounting for the marker width
            chars = self._chars_per_line(base_size, indent_pts)
            wrapped = textwrap.wrap(item_text, width=max(10, chars)) or [""]

            # First line: marker + text
            self._draw_line(prefix + wrapped[0])

            # Continuation lines: indented to align with text after the marker
            for cont in wrapped[1:]:
                old_x = self._x
                self._x += indent_pts
                self._draw_line(cont)
                self._x = old_x

        self.vspace(_SPACE_LIST)

    def force_new_page(self) -> None:
        """Emit a ``showpage`` and start a fresh page immediately."""
        self._end_page()
        self._start_page()

    def finalize(self) -> str:
        """Close the active page and return all accumulated PS commands joined."""
        self._end_page()
        return "\n".join(self.lines)


# ---------------------------------------------------------------------------
# Visitor
# ---------------------------------------------------------------------------

class PostScriptVisitor(NodeVisitor):
    """Traverses the AST and drives :class:`LayoutEngine` to produce PostScript.

    Parameters
    ----------
    base_font_size:
        The document's declared base font size in points.
    """

    def __init__(self, base_font_size: int = 12) -> None:
        self._engine           = LayoutEngine(base_font_size)
        self._base_size        = base_font_size
        self._section_count    = 0   # incremented on each SectionNode visit
        self._subsection_count = 0   # reset to 0 on each new section

    @property
    def engine(self) -> LayoutEngine:
        """The underlying :class:`LayoutEngine` instance."""
        return self._engine

    # ------------------------------------------------------------------
    # NodeVisitor implementation
    # ------------------------------------------------------------------

    def visit_document(self, node: DocumentNode) -> None:
        """Visit document root — recursively render all children."""
        for child in node.children:
            child.accept(self)

    def visit_title_page(self, node: TitlePageNode) -> None:
        self._engine.draw_title(node.title, node.style, self._base_size)

    def visit_chapter(self, node: ChapterNode) -> None:
        self._engine.draw_heading(node.title, level=1, base_size=self._base_size)
        for child in node.children:
            child.accept(self)

    def visit_section(self, node: SectionNode) -> None:
        self._section_count += 1
        self._subsection_count = 0
        numbered_title = f"{self._section_count}. {node.title}"
        self._engine.draw_heading(numbered_title, level=2, base_size=self._base_size)
        for child in node.children:
            child.accept(self)

    def visit_subsection(self, node: SubSectionNode) -> None:
        self._subsection_count += 1
        letter = chr(64 + self._subsection_count)  # 1→A, 2→B, …
        numbered_title = f"{letter}. {node.title}"
        self._engine.draw_heading(numbered_title, level=3, base_size=self._base_size)
        for child in node.children:
            child.accept(self)

    def visit_subsubsection(self, node: SubSubSectionNode) -> None:
        self._engine.draw_heading(node.title, level=4, base_size=self._base_size)
        for child in node.children:
            child.accept(self)

    def visit_text(self, node: TextNode) -> None:
        size = node.custom_size if node.custom_size is not None else self._base_size
        self._engine.draw_text(node.content, size, node.is_bold, node.is_italic)

    def visit_list(self, node: ListNode) -> None:
        """Collect item texts and delegate to the engine's list renderer."""
        item_texts = [item.content for item in node.children]
        self._engine.draw_list(item_texts, node.ordered, self._base_size)

    def visit_list_item(self, node: ListItemNode) -> None:
        # Individual items are handled by visit_list; a direct call is a no-op.
        pass

    def visit_new_page(self, node: NewPageNode) -> None:
        self._engine.force_new_page()


# ---------------------------------------------------------------------------
# PostScript document wrapper helpers
# ---------------------------------------------------------------------------

def _preamble(title: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return (
        f"%!PS-Adobe-3.0\n"
        f"%%Title: {title}\n"
        f"%%Creator: Cykaflex Compiler 0.3\n"
        f"%%CreationDate: {now}\n"
        f"%%Pages: (atend)\n"
        f"%%BoundingBox: 0 0 {_PAGE_W} {_PAGE_H}\n"
        f"%%EndComments\n"
        f"\n"
        f"%%BeginProlog\n"
        f"% --- Re-encode standard fonts to support Spanish (ISOLatin1) ---\n"
        f"/ReEncodeFont {{\n"
        f"  findfont\n"
        f"  dup length dict begin\n"
        f"    {{1 index /FID ne {{def}} {{pop pop}} ifelse}} forall\n"
        f"    /Encoding ISOLatin1Encoding def\n"
        f"    currentdict\n"
        f"  end\n"
        f"  definefont pop\n"
        f"}} bind def\n"
        f"\n"
        f"/Helvetica-Latin1 /Helvetica ReEncodeFont\n"
        f"/Helvetica-Bold-Latin1 /Helvetica-Bold ReEncodeFont\n"
        f"/Helvetica-Oblique-Latin1 /Helvetica-Oblique ReEncodeFont\n"
        f"/Helvetica-BoldOblique-Latin1 /Helvetica-BoldOblique ReEncodeFont\n"
        f"\n"
        f"% --- Macro para Justificar Texto Exacto ---\n"
        f"/JustifyShow {{\n"
        f"  2 dict begin\n"
        f"  /target_w exch def\n"
        f"  /str exch def\n"
        f"  str stringwidth pop /str_w exch def\n"
        f"  target_w str_w sub /gap exch def\n"
        f"  0 str {{ 32 eq {{ 1 add }} if }} forall /spaces exch def\n"
        f"  spaces 0 gt {{\n"
        f"    gap spaces div 0 32 str widthshow\n"
        f"  }} {{\n"
        f"    str show\n"
        f"  }} ifelse\n"
        f"  end\n"
        f"}} bind def\n"
        f"%%EndProlog\n"
        f"\n"
        f"%%BeginSetup\n"
        f"%%EndSetup\n"
        f"\n"
    )


def _trailer(pages: int) -> str:
    return f"\n%%Trailer\n%%Pages: {pages}\n%%EOF\n"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate(ast: DocumentNode, title: str = "Cykaflex Document") -> str:
    """Generate a complete PostScript document from *ast*.

    Parameters
    ----------
    ast:
        The root :class:`~.ast_nodes.DocumentNode` returned by the parser.
    title:
        Human-readable title placed in the ``%%Title`` DSC comment.

    Returns
    -------
    str
        A complete, valid PostScript-Adobe-3.0 document as a string.
        Save it with a ``.ps`` extension; open with Ghostscript or any
        PostScript viewer.

    Example
    -------
    ::

        from compiler.parser_ll1 import parse
        from compiler.codegen_postscript import generate

        with open("documento.cyk") as f:
            source = f.read()

        ps = generate(parse(source), title="Mi Artículo")

        with open("salida.ps", "w") as f:
            f.write(ps)
    """
    # Convert cm to pt when the document uses centimetre units
    if ast.font_unit == "cm":
        base_pt = round(ast.font_size * 72 / 2.54)
    else:
        base_pt = ast.font_size

    visitor = PostScriptVisitor(base_font_size=base_pt)
    ast.accept(visitor)

    body    = visitor.engine.finalize()
    pages   = visitor.engine.page

    return _preamble(title) + body + _trailer(pages)
