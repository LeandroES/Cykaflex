"""
Cykaflex Compiler API — main.py
================================
FastAPI application that exposes the Cykaflex compiler core over HTTP.

Pipeline per request
--------------------
    source (plain text)
        → Lexer        (lexer.py)
        → Parser LL(1) (parser_ll1.py)
        → AST
        → PostScript generator (codegen_postscript.py)
        → [optional] Ghostscript → PDF
        → HTTP response

Endpoints
---------
GET  /health            Liveness / readiness check.
POST /compile           Compile source → PS or PDF.
POST /tokenise          Return raw token stream (debug).
POST /ast               Return JSON AST (debug).

Error contract (HTTP 400)
-------------------------
Every compilation error is returned as::

    {
        "ok":         false,
        "error_type": "lex_error" | "parse_error",
        "line":       <int>,
        "col":        <int>,
        "detail":     "<human-readable message>"
    }
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from .compiler import LexError, ParseError, compile_to_ps, tokenise
from .compiler.parser_ll1 import parse

# ---------------------------------------------------------------------------
# Application setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Cykaflex Compiler API",
    description=(
        "Backend para el compilador del lenguaje de marcado tipográfico "
        "Cykaflex. Genera PostScript puro o PDF vía Ghostscript."
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Detect Ghostscript once at startup — result is cached for the lifetime of
# the process.  The `gs` binary is provided by the `ghostscript` apt package.
_GS_AVAILABLE: bool = shutil.which("gs") is not None


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class CompileRequest(BaseModel):
    """Payload for the /compile, /tokenise, and /ast endpoints."""

    source: str = Field(
        ...,
        description="Código fuente Cykaflex en texto plano.",
        examples=["clasedocumento[12pt]{articulo}\ninicio{documento}\nfin{documento}"],
    )
    title: str = Field(
        "Cykaflex Document",
        description="Título del documento (aparece en la cabecera %%Title del PS).",
    )
    output_format: Literal["ps", "pdf", "auto"] = Field(
        "auto",
        description=(
            "Formato de salida. "
            "'auto' devuelve PDF si Ghostscript está disponible, "
            "PS en caso contrario. "
            "'pdf' falla con 503 si Ghostscript no está instalado."
        ),
    )


class TokeniseResponse(BaseModel):
    tokens: list[dict]
    count: int


class ASTResponse(BaseModel):
    ok: bool = True
    ast: dict


class CompileErrorResponse(BaseModel):
    ok: bool = False
    error_type: Literal["lex_error", "parse_error"]
    line: int
    col: int
    detail: str


class HealthResponse(BaseModel):
    status: str
    version: str
    ghostscript: bool


# ---------------------------------------------------------------------------
# Exception handler — renders CompileErrorResponse for 400s
# ---------------------------------------------------------------------------

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return JSON for every HTTPException, including 400 compilation errors."""
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "detail": str(exc.detail)},
    )


# ---------------------------------------------------------------------------
# Ghostscript helper
# ---------------------------------------------------------------------------

def _ps_to_pdf(ps_source: str) -> bytes:
    """Convert PostScript source to PDF bytes using the ``gs`` binary.

    Parameters
    ----------
    ps_source:
        Complete, valid PostScript document as a string.

    Returns
    -------
    bytes
        Raw PDF bytes ready to be streamed to the client.

    Raises
    ------
    RuntimeError
        When ``gs`` exits with a non-zero return code.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        ps_path  = Path(tmpdir) / "input.ps"
        pdf_path = Path(tmpdir) / "output.pdf"

        ps_path.write_text(ps_source, encoding="utf-8")

        result = subprocess.run(
            [
                "gs",
                "-dBATCH",           # exit after processing
                "-dNOPAUSE",         # no pause between pages
                "-dSAFER",           # restrict PS filesystem access
                "-dQUIET",           # suppress informational messages
                "-sDEVICE=pdfwrite",
                f"-sOutputFile={pdf_path}",
                str(ps_path),
            ],
            capture_output=True,
            timeout=30,
        )

        if result.returncode != 0:
            stderr = result.stderr.decode(errors="replace")
            raise RuntimeError(f"Ghostscript falló (código {result.returncode}): {stderr}")

        return pdf_path.read_bytes()


# ---------------------------------------------------------------------------
# Helpers for structured error responses
# ---------------------------------------------------------------------------

def _lex_400(exc: LexError) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "ok":         False,
            "error_type": "lex_error",
            "line":       exc.line,
            "col":        exc.col,
            "detail":     str(exc),
        },
    )


def _parse_400(exc: ParseError) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail={
            "ok":         False,
            "error_type": "parse_error",
            "line":       exc.line,
            "col":        exc.col,
            "detail":     str(exc),
        },
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["status"])
def health() -> HealthResponse:
    """Liveness / readiness check.

    Also reports whether Ghostscript is available (i.e. PDF output is
    supported on this instance).
    """
    return HealthResponse(
        status="ok",
        version="0.2.0",
        ghostscript=_GS_AVAILABLE,
    )


@app.post(
    "/compile",
    tags=["compiler"],
    responses={
        200: {
            "description": "Documento PostScript o PDF compilado correctamente.",
            "content": {
                "application/postscript": {"schema": {"type": "string", "format": "binary"}},
                "application/pdf":        {"schema": {"type": "string", "format": "binary"}},
            },
        },
        400: {"model": CompileErrorResponse, "description": "Error léxico o sintáctico."},
        503: {"description": "Ghostscript no disponible (sólo cuando format=pdf)."},
    },
)
def compile_source(req: CompileRequest) -> Response:
    """Compile Cykaflex source and return a PostScript or PDF document.

    The pipeline runs synchronously in FastAPI's thread-pool executor so
    the event loop is never blocked.

    **Format negotiation** (``output_format`` field):

    * ``"auto"`` — returns PDF if Ghostscript is installed, PS otherwise.
    * ``"ps"``   — always returns PostScript (``application/postscript``).
    * ``"pdf"``  — returns PDF; fails with HTTP 503 if Ghostscript is absent.
    """
    # ── 1. Compile to PostScript ──────────────────────────────────────────
    try:
        ps = compile_to_ps(req.source, title=req.title)
    except LexError as exc:
        raise _lex_400(exc) from exc
    except ParseError as exc:
        raise _parse_400(exc) from exc

    # ── 2. Negotiate output format ────────────────────────────────────────
    want_pdf = req.output_format == "pdf" or (
        req.output_format == "auto" and _GS_AVAILABLE
    )

    if want_pdf and not _GS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail=(
                "Ghostscript no está instalado en este servidor. "
                "Use output_format='ps' para obtener PostScript."
            ),
        )

    if want_pdf:
        try:
            pdf_bytes = _ps_to_pdf(ps)
        except RuntimeError as exc:
            # GS is installed but failed on this specific document
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="documento.pdf"',
                "X-Cykaflex-Format": "pdf",
            },
        )

    # Fall back to (or explicitly return) PostScript
    return Response(
        content=ps,
        media_type="application/postscript",
        headers={
            "Content-Disposition": 'attachment; filename="documento.ps"',
            "X-Cykaflex-Format": "ps",
        },
    )


@app.post("/tokenise", response_model=TokeniseResponse, tags=["debug"])
def tokenise_source(req: CompileRequest) -> TokeniseResponse:
    """Return the raw token stream produced by the Cykaflex lexer.

    Useful for inspecting tokenisation and debugging lexical errors
    without running the full parse / codegen pipeline.
    """
    try:
        toks = tokenise(req.source)
    except LexError as exc:
        raise _lex_400(exc) from exc

    token_list = [
        {
            "type":   t.type,
            "value":  t.value,
            "line":   t.lineno,
            "col":    t.lexpos,
        }
        for t in toks
    ]
    return TokeniseResponse(tokens=token_list, count=len(token_list))


@app.post("/ast", response_model=ASTResponse, tags=["debug"])
def parse_ast(req: CompileRequest) -> ASTResponse:
    """Parse *source* and return a JSON tree representation of the AST.

    Each node is serialised as ``{"type": "<ClassName>", ...fields...}``.
    Children are nested recursively.
    """
    try:
        ast = parse(req.source)
    except LexError as exc:
        raise _lex_400(exc) from exc
    except ParseError as exc:
        raise _parse_400(exc) from exc

    def _to_dict(node: object) -> dict:  # type: ignore[type-arg]
        result: dict = {"type": type(node).__name__}
        for key, val in vars(node).items():
            result[key] = (
                [_to_dict(child) for child in val]
                if isinstance(val, list)
                else val
            )
        return result

    return ASTResponse(ast=_to_dict(ast))
