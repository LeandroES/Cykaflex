"""
Cykaflex AST Nodes
==================
**Composite pattern** for the Cykaflex Abstract Syntax Tree.

Every concrete node inherits from :class:`ASTNode` and implements
``accept(visitor)`` so that any :class:`NodeVisitor` can traverse the tree
without modifying the nodes themselves (**Visitor pattern**).

Node hierarchy
--------------
::

    ASTNode (abstract)
    ├── DocumentNode          — root, holds doc-class metadata
    ├── TitlePageNode         — titulopagina[style]{"Title"}
    ├── ChapterNode           — capitulo["Title"]{ body }
    ├── SectionNode           — seccion["Title"]{ body }
    ├── SubSectionNode        — subseccion["Title"]{ body }
    ├── SubSubSectionNode     — subsubseccion["Title"]{ body }
    ├── TextNode              — texto[Npt][negrita][cursiva]{"content"} (all modifiers optional)
    ├── ListNode              — inicioe/inicioi list container
    ├── ListItemNode          — item{"content"}
    └── NewPageNode           — nuevapagina
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Abstract base types
# ---------------------------------------------------------------------------

class ASTNode(ABC):
    """Abstract base class for every node in the Cykaflex AST."""

    @abstractmethod
    def accept(self, visitor: "NodeVisitor") -> None:
        """Dispatch to the appropriate ``visit_*`` method of *visitor*."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class NodeVisitor(ABC):
    """Abstract visitor interface.

    Concrete visitors (e.g. the PostScript code generator) implement
    every ``visit_*`` method declared here.
    """

    @abstractmethod
    def visit_document(self, node: "DocumentNode") -> None: ...

    @abstractmethod
    def visit_title_page(self, node: "TitlePageNode") -> None: ...

    @abstractmethod
    def visit_chapter(self, node: "ChapterNode") -> None: ...

    @abstractmethod
    def visit_section(self, node: "SectionNode") -> None: ...

    @abstractmethod
    def visit_subsection(self, node: "SubSectionNode") -> None: ...

    @abstractmethod
    def visit_subsubsection(self, node: "SubSubSectionNode") -> None: ...

    @abstractmethod
    def visit_text(self, node: "TextNode") -> None: ...

    @abstractmethod
    def visit_list(self, node: "ListNode") -> None: ...

    @abstractmethod
    def visit_list_item(self, node: "ListItemNode") -> None: ...

    @abstractmethod
    def visit_new_page(self, node: "NewPageNode") -> None: ...


# ---------------------------------------------------------------------------
# Concrete AST node classes
# ---------------------------------------------------------------------------

@dataclass
class DocumentNode(ASTNode):
    """Root node of the entire document.

    Attributes
    ----------
    doc_type:
        ``'articulo'`` or ``'libro'``.
    font_size:
        Base font size extracted from ``clasedocumento[NNpt]{...}``.
    font_unit:
        Unit of *font_size*: ``'pt'`` or ``'cm'``.
    children:
        Top-level content elements in document order.
    """

    doc_type: str
    font_size: int
    font_unit: str
    children: list[ASTNode] = field(default_factory=list)

    def accept(self, visitor: NodeVisitor) -> None:
        visitor.visit_document(self)

    def __repr__(self) -> str:
        return (
            f"DocumentNode(doc_type={self.doc_type!r}, "
            f"font_size={self.font_size}{self.font_unit}, "
            f"children={len(self.children)})"
        )


@dataclass
class TitlePageNode(ASTNode):
    """Represents a ``titulopagina[style]{"Title"}`` directive.

    Attributes
    ----------
    title:
        The content string (without surrounding quotes).
    style:
        ``'negrita'``, ``'cursiva'``, or ``''`` when no style is present.
    """

    title: str
    style: str = ""

    def accept(self, visitor: NodeVisitor) -> None:
        visitor.visit_title_page(self)

    def __repr__(self) -> str:
        return f"TitlePageNode(title={self.title!r}, style={self.style!r})"


@dataclass
class ChapterNode(ASTNode):
    """Represents a ``capitulo["Title"]{ body }`` block.

    Attributes
    ----------
    title:
        Chapter heading text.
    children:
        Block elements that form the chapter body.
    """

    title: str
    children: list[ASTNode] = field(default_factory=list)

    def accept(self, visitor: NodeVisitor) -> None:
        visitor.visit_chapter(self)

    def __repr__(self) -> str:
        return f"ChapterNode(title={self.title!r}, children={len(self.children)})"


@dataclass
class SectionNode(ASTNode):
    """Represents a ``seccion["Title"]{ body }`` block."""

    title: str
    children: list[ASTNode] = field(default_factory=list)

    def accept(self, visitor: NodeVisitor) -> None:
        visitor.visit_section(self)

    def __repr__(self) -> str:
        return f"SectionNode(title={self.title!r}, children={len(self.children)})"


@dataclass
class SubSectionNode(ASTNode):
    """Represents a ``subseccion["Title"]{ body }`` block."""

    title: str
    children: list[ASTNode] = field(default_factory=list)

    def accept(self, visitor: NodeVisitor) -> None:
        visitor.visit_subsection(self)

    def __repr__(self) -> str:
        return f"SubSectionNode(title={self.title!r}, children={len(self.children)})"


@dataclass
class SubSubSectionNode(ASTNode):
    """Represents a ``subsubseccion["Title"]{ body }`` block."""

    title: str
    children: list[ASTNode] = field(default_factory=list)

    def accept(self, visitor: NodeVisitor) -> None:
        visitor.visit_subsubsection(self)

    def __repr__(self) -> str:
        return f"SubSubSectionNode(title={self.title!r}, children={len(self.children)})"


@dataclass
class TextNode(ASTNode):
    """Represents a ``texto`` directive, optionally with inline modifiers.

    Syntax variants (modifiers may appear in any order)::

        texto{"content"}
        texto[12pt]{"content"}
        texto[negrita]{"content"}
        texto[cursiva]{"content"}
        texto[14pt][negrita][cursiva]{"content"}

    Attributes
    ----------
    content:
        The raw text string without surrounding quotes.
    custom_size:
        Optional font size override in points.  When ``None`` the document's
        base font size is used instead.
    is_bold:
        When ``True`` the paragraph is rendered in bold (Helvetica-Bold or
        Helvetica-BoldOblique when combined with *is_italic*).
    is_italic:
        When ``True`` the paragraph is rendered in italic (Helvetica-Oblique or
        Helvetica-BoldOblique when combined with *is_bold*).
    """

    content: str
    custom_size: int | None = None
    is_bold: bool = False
    is_italic: bool = False

    def accept(self, visitor: NodeVisitor) -> None:
        visitor.visit_text(self)

    def __repr__(self) -> str:
        preview = self.content[:40] + "…" if len(self.content) > 40 else self.content
        mods: list[str] = []
        if self.custom_size is not None:
            mods.append(f"size={self.custom_size}pt")
        if self.is_bold:
            mods.append("bold")
        if self.is_italic:
            mods.append("italic")
        suffix = (", " + ", ".join(mods)) if mods else ""
        return f"TextNode({preview!r}{suffix})"


@dataclass
class ListNode(ASTNode):
    """An ordered (enumerated) or unordered (itemized) list.

    Attributes
    ----------
    ordered:
        ``True``  → numbered list (``inicioe[ennumerar]{...}``).
        ``False`` → bulleted list (``inicioi[itemizar]{...}``).
    children:
        :class:`ListItemNode` instances in order.
    """

    ordered: bool
    children: list["ListItemNode"] = field(default_factory=list)

    def accept(self, visitor: NodeVisitor) -> None:
        visitor.visit_list(self)

    def __repr__(self) -> str:
        kind = "ordered" if self.ordered else "unordered"
        return f"ListNode({kind}, items={len(self.children)})"


@dataclass
class ListItemNode(ASTNode):
    """A single ``item{"content"}`` entry inside a list."""

    content: str

    def accept(self, visitor: NodeVisitor) -> None:
        visitor.visit_list_item(self)

    def __repr__(self) -> str:
        return f"ListItemNode(content={self.content!r})"


@dataclass
class NewPageNode(ASTNode):
    """Represents a ``nuevapagina`` directive — forces a page break."""

    def accept(self, visitor: NodeVisitor) -> None:
        visitor.visit_new_page(self)
