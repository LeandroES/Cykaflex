"""
Cykaflex LL(1) Recursive-Descent Parser
========================================
Consumes the token stream produced by :mod:`.lexer` and constructs an
Abstract Syntax Tree made of :mod:`.ast_nodes` instances.

Grammar (formal — derived from ``input.txt`` and verified against examples)
----------------------------------------------------------------------------
::

    programa            → clasedocumento bloque_documento

    clasedocumento      → CLASEDOCUMENTO LEFT_BRACKET NUMBER metrics
                          RIGHT_BRACKET LEFT_KEY doc_type RIGHT_KEY
    metrics             → PT | CM
    doc_type            → ARTICULO | LIBRO

    bloque_documento    → INICIO LEFT_KEY DOCUMENTO RIGHT_KEY
                          cuerpo
                          FIN LEFT_KEY DOCUMENTO RIGHT_KEY

    cuerpo              → elemento cuerpo | ε

    elemento            → titulo
                        | capitulo
                        | seccion
                        | subseccion
                        | subsubseccion
                        | texto
                        | lista
                        | NUEVAPAGINA
                        | COMMENT          (discarded)

    titulo              → TITULOPAGINA LEFT_BRACKET style RIGHT_BRACKET
                          LEFT_KEY CONTENT RIGHT_KEY
    style               → NEGRITA | CURSIVA

    capitulo            → CAPITULO LEFT_BRACKET CONTENT RIGHT_BRACKET
                          LEFT_KEY cuerpo RIGHT_KEY

    seccion             → SECCION LEFT_BRACKET CONTENT RIGHT_BRACKET
                          LEFT_KEY cuerpo RIGHT_KEY

    subseccion          → SUBSECCION LEFT_BRACKET CONTENT RIGHT_BRACKET
                          LEFT_KEY cuerpo RIGHT_KEY

    subsubseccion       → SUBSUBSECCION LEFT_BRACKET CONTENT RIGHT_BRACKET
                          LEFT_KEY cuerpo RIGHT_KEY

    texto               → TEXTO LEFT_KEY CONTENT RIGHT_KEY

    lista               → enumerar | itemizar
    enumerar            → INICIOE LEFT_BRACKET ENNUMERAR RIGHT_BRACKET
                          LEFT_KEY items RIGHT_KEY
    itemizar            → INICIOI LEFT_BRACKET ITEMIZAR RIGHT_BRACKET
                          LEFT_KEY items RIGHT_KEY
    items               → item items | ε
    item                → ITEM LEFT_KEY CONTENT RIGHT_KEY

Key design notes
----------------
* Cuerpo parsing stops on ``RIGHT_KEY`` (end of enclosing block) or ``FIN``.
* COMMENT tokens are silently dropped — they never appear in the AST.
* ``_expect()`` raises :exc:`ParseError` with a human-readable line number.
"""

from __future__ import annotations

from typing import Any

from .ast_nodes import (
    ASTNode,
    ChapterNode,
    DocumentNode,
    ListItemNode,
    ListNode,
    NewPageNode,
    SectionNode,
    SubSectionNode,
    SubSubSectionNode,
    TextNode,
    TitlePageNode,
)
from .lexer import LexError, tokenise  # noqa: F401 — re-exported for callers


class ParseError(Exception):
    """Raised when the parser encounters an unexpected token or EOF."""


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class CykafParser:
    """Recursive-descent LL(1) parser for the Cykaflex language.

    Each grammar rule is implemented as a private ``_parse_*`` method.
    The parser holds a flat token list and a position index; there is no
    lookahead buffer — the current token is simply ``self._current``.

    Usage::

        ast = CykafParser().parse(source_code)
    """

    def __init__(self) -> None:
        self._tokens: list[Any] = []
        self._pos: int = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, source: str) -> DocumentNode:
        """Parse *source* and return the root :class:`DocumentNode`.

        Parameters
        ----------
        source:
            Raw Cykaflex source code.

        Returns
        -------
        DocumentNode
            The fully constructed AST root.

        Raises
        ------
        LexError
            On lexical errors in *source*.
        ParseError
            On syntactic errors in *source*.
        """
        self._tokens = tokenise(source)
        self._pos = 0
        return self._parse_programa()

    # ------------------------------------------------------------------
    # Internal token-stream helpers
    # ------------------------------------------------------------------

    @property
    def _current(self) -> Any | None:
        """The current token, or ``None`` at end of stream."""
        return self._tokens[self._pos] if self._pos < len(self._tokens) else None

    @property
    def _current_type(self) -> str:
        """Token type of the current token, or ``'EOF'``."""
        tok = self._current
        return tok.type if tok is not None else "EOF"

    def _advance(self) -> Any:
        """Consume and return the current token."""
        tok = self._current
        self._pos += 1
        return tok

    def _expect(self, *token_types: str) -> Any:
        """Consume the current token only if its type is in *token_types*.

        Raises
        ------
        ParseError
            With a descriptive message including the line number.
        """
        if self._current_type not in token_types:
            expected = " | ".join(token_types)
            if self._current is not None:
                got = f"'{self._current.value}' ({self._current_type})"
                line = self._current.lineno
            else:
                got, line = "EOF", "?"
            raise ParseError(
                f"Línea {line}: se esperaba {expected}, se encontró {got}"
            )
        return self._advance()

    def _skip_comments(self) -> None:
        """Advance past any consecutive COMMENT tokens."""
        while self._current_type == "COMMENT":
            self._advance()

    # ------------------------------------------------------------------
    # Grammar rules — one method per non-terminal
    # ------------------------------------------------------------------

    def _parse_programa(self) -> DocumentNode:
        """programa → clasedocumento bloque_documento"""
        self._skip_comments()
        doc = self._parse_clasedocumento()
        self._skip_comments()
        doc.children = self._parse_bloque_documento()
        return doc

    # ── Document class declaration ──────────────────────────────────────

    def _parse_clasedocumento(self) -> DocumentNode:
        """clasedocumento → CLASEDOCUMENTO LEFT_BRACKET NUMBER metrics
                            RIGHT_BRACKET LEFT_KEY doc_type RIGHT_KEY
        """
        self._expect("CLASEDOCUMENTO")
        self._expect("LEFT_BRACKET")
        size_tok = self._expect("NUMBER")
        font_size: int = size_tok.value
        unit_tok = self._expect("PT", "CM")
        font_unit: str = "pt" if unit_tok.type == "PT" else "cm"
        self._expect("RIGHT_BRACKET")
        self._expect("LEFT_KEY")
        doc_type_tok = self._expect("ARTICULO", "LIBRO")
        doc_type: str = doc_type_tok.value   # 'articulo' | 'libro'
        self._expect("RIGHT_KEY")
        return DocumentNode(doc_type=doc_type, font_size=font_size, font_unit=font_unit)

    # ── Document body ───────────────────────────────────────────────────

    def _parse_bloque_documento(self) -> list[ASTNode]:
        """bloque_documento → INICIO LEFT_KEY DOCUMENTO RIGHT_KEY
                               cuerpo
                               FIN LEFT_KEY DOCUMENTO RIGHT_KEY
        """
        self._expect("INICIO")
        self._expect("LEFT_KEY")
        self._expect("DOCUMENTO")
        self._expect("RIGHT_KEY")
        children = self._parse_cuerpo()
        self._expect("FIN")
        self._expect("LEFT_KEY")
        self._expect("DOCUMENTO")
        self._expect("RIGHT_KEY")
        return children

    def _parse_cuerpo(self) -> list[ASTNode]:
        """cuerpo → elemento cuerpo | ε

        Parses elements until a RIGHT_KEY (end of an enclosing block),
        a FIN keyword, or end of stream.
        """
        nodes: list[ASTNode] = []
        while self._current_type not in {"RIGHT_KEY", "FIN", "EOF"}:
            self._skip_comments()
            if self._current_type in {"RIGHT_KEY", "FIN", "EOF"}:
                break
            node = self._parse_elemento()
            if node is not None:
                nodes.append(node)
        return nodes

    def _parse_elemento(self) -> ASTNode | None:
        """Dispatch to the correct rule based on the current token."""
        dispatch: dict[str, Any] = {
            "TITULOPAGINA":   self._parse_titulo,
            "CAPITULO":       self._parse_capitulo,
            "SECCION":        self._parse_seccion,
            "SUBSECCION":     self._parse_subseccion,
            "SUBSUBSECCION":  self._parse_subsubseccion,
            "TEXTO":          self._parse_texto,
            "INICIOE":        self._parse_enumerar,
            "INICIOI":        self._parse_itemizar,
        }
        t = self._current_type

        if t in dispatch:
            return dispatch[t]()

        if t == "NUEVAPAGINA":
            self._advance()
            return NewPageNode()

        if t == "COMMENT":
            self._advance()
            return None  # silently discarded

        tok = self._current
        line = tok.lineno if tok else "?"
        value = tok.value if tok else "EOF"
        raise ParseError(
            f"Línea {line}: token inesperado '{value}' ({t}) "
            f"al inicio de un elemento"
        )

    # ── Block elements ──────────────────────────────────────────────────

    def _parse_titulo(self) -> TitlePageNode:
        """titulo → TITULOPAGINA LEFT_BRACKET style RIGHT_BRACKET
                     LEFT_KEY CONTENT RIGHT_KEY
        """
        self._expect("TITULOPAGINA")
        self._expect("LEFT_BRACKET")
        style_tok = self._expect("NEGRITA", "CURSIVA")
        style: str = style_tok.value
        self._expect("RIGHT_BRACKET")
        self._expect("LEFT_KEY")
        content_tok = self._expect("CONTENT")
        self._expect("RIGHT_KEY")
        return TitlePageNode(title=content_tok.value, style=style)

    def _parse_capitulo(self) -> ChapterNode:
        """capitulo → CAPITULO LEFT_BRACKET CONTENT RIGHT_BRACKET
                       LEFT_KEY cuerpo RIGHT_KEY
        """
        self._expect("CAPITULO")
        self._expect("LEFT_BRACKET")
        title_tok = self._expect("CONTENT")
        self._expect("RIGHT_BRACKET")
        self._expect("LEFT_KEY")
        children = self._parse_cuerpo()
        self._expect("RIGHT_KEY")
        return ChapterNode(title=title_tok.value, children=children)

    def _parse_seccion(self) -> SectionNode:
        """seccion → SECCION LEFT_BRACKET CONTENT RIGHT_BRACKET
                      LEFT_KEY cuerpo RIGHT_KEY
        """
        self._expect("SECCION")
        self._expect("LEFT_BRACKET")
        title_tok = self._expect("CONTENT")
        self._expect("RIGHT_BRACKET")
        self._expect("LEFT_KEY")
        children = self._parse_cuerpo()
        self._expect("RIGHT_KEY")
        return SectionNode(title=title_tok.value, children=children)

    def _parse_subseccion(self) -> SubSectionNode:
        """subseccion → SUBSECCION LEFT_BRACKET CONTENT RIGHT_BRACKET
                         LEFT_KEY cuerpo RIGHT_KEY
        """
        self._expect("SUBSECCION")
        self._expect("LEFT_BRACKET")
        title_tok = self._expect("CONTENT")
        self._expect("RIGHT_BRACKET")
        self._expect("LEFT_KEY")
        children = self._parse_cuerpo()
        self._expect("RIGHT_KEY")
        return SubSectionNode(title=title_tok.value, children=children)

    def _parse_subsubseccion(self) -> SubSubSectionNode:
        """subsubseccion → SUBSUBSECCION LEFT_BRACKET CONTENT RIGHT_BRACKET
                            LEFT_KEY cuerpo RIGHT_KEY
        """
        self._expect("SUBSUBSECCION")
        self._expect("LEFT_BRACKET")
        title_tok = self._expect("CONTENT")
        self._expect("RIGHT_BRACKET")
        self._expect("LEFT_KEY")
        children = self._parse_cuerpo()
        self._expect("RIGHT_KEY")
        return SubSubSectionNode(title=title_tok.value, children=children)

    def _parse_texto(self) -> TextNode:
        """texto → TEXTO LEFT_KEY CONTENT RIGHT_KEY"""
        self._expect("TEXTO")
        self._expect("LEFT_KEY")
        content_tok = self._expect("CONTENT")
        self._expect("RIGHT_KEY")
        return TextNode(content=content_tok.value)

    # ── List elements ───────────────────────────────────────────────────

    def _parse_enumerar(self) -> ListNode:
        """enumerar → INICIOE LEFT_BRACKET ENNUMERAR RIGHT_BRACKET
                       LEFT_KEY items RIGHT_KEY
        """
        self._expect("INICIOE")
        self._expect("LEFT_BRACKET")
        self._expect("ENNUMERAR")
        self._expect("RIGHT_BRACKET")
        self._expect("LEFT_KEY")
        items = self._parse_items()
        self._expect("RIGHT_KEY")
        return ListNode(ordered=True, children=items)

    def _parse_itemizar(self) -> ListNode:
        """itemizar → INICIOI LEFT_BRACKET ITEMIZAR RIGHT_BRACKET
                       LEFT_KEY items RIGHT_KEY
        """
        self._expect("INICIOI")
        self._expect("LEFT_BRACKET")
        self._expect("ITEMIZAR")
        self._expect("RIGHT_BRACKET")
        self._expect("LEFT_KEY")
        items = self._parse_items()
        self._expect("RIGHT_KEY")
        return ListNode(ordered=False, children=items)

    def _parse_items(self) -> list[ListItemNode]:
        """items → item items | ε"""
        items: list[ListItemNode] = []
        self._skip_comments()
        while self._current_type == "ITEM":
            items.append(self._parse_item())
            self._skip_comments()
        return items

    def _parse_item(self) -> ListItemNode:
        """item → ITEM LEFT_KEY CONTENT RIGHT_KEY"""
        self._expect("ITEM")
        self._expect("LEFT_KEY")
        content_tok = self._expect("CONTENT")
        self._expect("RIGHT_KEY")
        return ListItemNode(content=content_tok.value)


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------

def parse(source: str) -> DocumentNode:
    """Parse *source* and return the AST root.

    Parameters
    ----------
    source:
        Raw Cykaflex source code string.

    Returns
    -------
    DocumentNode
        The fully constructed AST root node.

    Raises
    ------
    LexError
        On lexical errors.
    ParseError
        On syntactic errors.
    """
    return CykafParser().parse(source)
