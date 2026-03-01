"""
compiler — Cykaflex compiler core package
==========================================
Provides the full pipeline:  source → tokens → AST → PostScript

Public API::

    from compiler import compile_to_ps

    ps_source = compile_to_ps(cykaflex_source, title="Mi Documento")

Modules
-------
lexer               PLY-based lexical analyser
ast_nodes           AST node classes (Composite + Visitor pattern)
parser_ll1          Recursive-descent LL(1) parser
codegen_postscript  PostScript code generator (Visitor)
"""

from .codegen_postscript import generate
from .lexer import LexError, tokenise
from .parser_ll1 import CykafParser, ParseError, parse


def compile_to_ps(source: str, title: str = "Cykaflex Document") -> str:
    """Run the full compilation pipeline on *source*.

    Parameters
    ----------
    source:
        Raw Cykaflex source code.
    title:
        Document title placed in the PostScript ``%%Title`` header.

    Returns
    -------
    str
        A complete, valid PostScript document string.

    Raises
    ------
    LexError
        On lexical errors in *source*.
    ParseError
        On syntactic errors in *source*.
    """
    ast = parse(source)
    return generate(ast, title=title)


__all__ = [
    "compile_to_ps",
    "generate",
    "parse",
    "tokenise",
    "CykafParser",
    "LexError",
    "ParseError",
]
