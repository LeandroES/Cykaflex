"""
Cykaflex Lexer
==============
PLY-based lexical analyser for the Cykaflex typographic markup language.

Token reference
---------------
Symbols  : RIGHT_KEY ``}``  LEFT_KEY ``{``  RIGHT_BRACKET ``]``  LEFT_BRACKET ``[``
Literals : CONTENT (double-quoted string),  NUMBER (integer),  COMMENT (``%`` line)
Keywords : see ``_RESERVED`` dict — one token type per keyword

Example source fragment::

    clasedocumento[12pt]{articulo}
    inicio{documento}
    titulopagina[negrita]{"Hello World"}
    fin{documento}
"""

from __future__ import annotations

from typing import Any

import ply.lex as lex  # type: ignore[import-untyped]

# ---------------------------------------------------------------------------
# Reserved words — source spelling → PLY token type
# ---------------------------------------------------------------------------

_RESERVED: dict[str, str] = {
    "cm":             "CM",
    "pt":             "PT",
    "item":           "ITEM",
    "inicio":         "INICIO",
    "fin":            "FIN",
    "documento":      "DOCUMENTO",
    "titulopagina":   "TITULOPAGINA",
    "ennumerar":      "ENNUMERAR",
    "itemizar":       "ITEMIZAR",
    "inicioe":        "INICIOE",
    "inicioi":        "INICIOI",
    "negrita":        "NEGRITA",
    "cursiva":        "CURSIVA",
    "seccion":        "SECCION",
    "subseccion":     "SUBSECCION",
    "subsubseccion":  "SUBSUBSECCION",
    "nuevapagina":    "NUEVAPAGINA",
    "clasedocumento": "CLASEDOCUMENTO",
    "articulo":       "ARTICULO",
    "libro":          "LIBRO",
    "capitulo":       "CAPITULO",
    "texto":          "TEXTO",
}

# PLY requires a module-level tuple called ``tokens``.
# ``dict.fromkeys`` preserves insertion order while deduplicating values.
tokens: tuple[str, ...] = (
    "RIGHT_KEY",
    "LEFT_KEY",
    "RIGHT_BRACKET",
    "LEFT_BRACKET",
    "CONTENT",
    "NUMBER",
    "COMMENT",
) + tuple(dict.fromkeys(_RESERVED.values()))


# ---------------------------------------------------------------------------
# Simple symbol rules — PLY matches string patterns by decreasing length
# ---------------------------------------------------------------------------

t_RIGHT_KEY     = r"\}"
t_LEFT_KEY      = r"\{"
t_RIGHT_BRACKET = r"\]"
t_LEFT_BRACKET  = r"\["

# Characters to silently ignore (spaces and horizontal tabs)
t_ignore = " \t\r"


# ---------------------------------------------------------------------------
# Function-based rules — matched in definition order; longer patterns first
# ---------------------------------------------------------------------------

def t_CONTENT(t: Any) -> Any:
    r'"[^"\n]*"'
    t.value = t.value[1:-1]  # strip surrounding double-quotes
    return t


def t_COMMENT(t: Any) -> Any:
    r'%[^\n]*'
    # Yielded to the parser so it can discard comments explicitly;
    # keeping the token ensures line-number tracking stays correct.
    return t


def t_NUMBER(t: Any) -> Any:
    r'[0-9]+'
    t.value = int(t.value)
    return t


def t_WORD(t: Any) -> Any:
    r'[a-zA-Z][a-zA-Z0-9]*'
    token_type = _RESERVED.get(t.value)
    if token_type is None:
        raise LexError(
            f"Identificador desconocido '{t.value}' en línea {t.lineno}"
        )
    t.type = token_type
    return t


def t_newline(t: Any) -> Any:
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t: Any) -> None:
    raise LexError(
        f"Carácter ilegal '{t.value[0]}' "
        f"en línea {t.lineno}, posición {t.lexpos}"
    )


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

class LexError(Exception):
    """Raised when the lexer encounters an unexpected character or identifier."""


def build_lexer(*, debug: bool = False) -> lex.Lexer:
    """Build and return a fresh PLY Lexer instance.

    Parameters
    ----------
    debug:
        Pass ``True`` to enable PLY's built-in debug output.
    """
    return lex.lex(debug=debug, errorlog=lex.NullLogger())


def tokenise(source: str) -> list[Any]:
    """Tokenise *source* and return an ordered list of PLY token objects.

    Parameters
    ----------
    source:
        Raw Cykaflex source code.

    Returns
    -------
    list[LexToken]
        Token list ready to be consumed by the parser.

    Raises
    ------
    LexError
        On any lexical error (unknown identifier or illegal character).
    """
    lexer = build_lexer()
    lexer.input(source)
    result: list[Any] = []
    while True:
        tok = lexer.token()
        if tok is None:
            break
        result.append(tok)
    return result
