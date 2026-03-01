"""
Cykaflex Compiler API
======================
FastAPI backend that exposes the Cykaflex compiler core over HTTP.

Endpoints
---------
GET  /health        Liveness check.
POST /compile       Compile Cykaflex source → PostScript.
POST /tokenise      Return the token stream (useful for debugging).
POST /ast           Return a JSON representation of the AST.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .compiler import LexError, ParseError, compile_to_ps, tokenise
from .compiler.parser_ll1 import parse

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Cykaflex Compiler API",
    description=(
        "Backend para el compilador del lenguaje de marcado "
        "tipográfico Cykaflex. Genera PostScript puro."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class CompileRequest(BaseModel):
    source: str
    title: str = "Cykaflex Document"


class CompileResponse(BaseModel):
    postscript: str
    pages: int
    ok: bool = True


class TokeniseResponse(BaseModel):
    tokens: list[dict]
    count: int


class ASTResponse(BaseModel):
    ast: dict
    ok: bool = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", tags=["status"])
def health() -> dict:
    """Liveness check — always returns 200 when the service is running."""
    return {"status": "ok", "service": "Cykaflex Compiler API", "version": "0.1.0"}


@app.post("/compile", response_model=CompileResponse, tags=["compiler"])
def compile_source(req: CompileRequest) -> CompileResponse:
    """Compile Cykaflex *source* and return a PostScript document.

    The PostScript string can be saved directly as a ``.ps`` file and
    opened with Ghostscript or any PostScript viewer.
    """
    try:
        ps = compile_to_ps(req.source, title=req.title)
    except (LexError, ParseError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Count pages by the number of %%Page: DSC comments
    pages = ps.count("%%Page:")
    return CompileResponse(postscript=ps, pages=pages)


@app.post("/tokenise", response_model=TokeniseResponse, tags=["debug"])
def tokenise_source(req: CompileRequest) -> TokeniseResponse:
    """Return the raw token stream produced by the lexer.

    Useful for inspecting how the source is tokenised and for debugging
    lexical errors.
    """
    try:
        toks = tokenise(req.source)
    except LexError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    token_list = [
        {"type": t.type, "value": t.value, "line": t.lineno, "pos": t.lexpos}
        for t in toks
    ]
    return TokeniseResponse(tokens=token_list, count=len(token_list))


@app.post("/ast", response_model=ASTResponse, tags=["debug"])
def parse_ast(req: CompileRequest) -> ASTResponse:
    """Parse *source* and return a JSON representation of the AST.

    Each node is serialised as ``{"type": "<ClassName>", ...fields...}``.
    """
    try:
        ast = parse(req.source)
    except (LexError, ParseError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    def _node_to_dict(node) -> dict:  # type: ignore[no-untyped-def]
        result: dict = {"type": type(node).__name__}
        for field, value in vars(node).items():
            if isinstance(value, list):
                result[field] = [_node_to_dict(c) for c in value]
            else:
                result[field] = value
        return result

    return ASTResponse(ast=_node_to_dict(ast))
