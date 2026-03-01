from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Cykaflex Compiler API",
    description="Backend para el compilador del lenguaje de marcado tipográfico Cykaflex",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["status"])
def health():
    return {"status": "ok", "service": "Cykaflex Compiler API"}


@app.post("/compile", tags=["compiler"])
async def compile_source(source: dict):
    """
    Recibe código fuente Cykaflex y retorna el resultado del análisis.
    Endpoint a implementar — conectará con el núcleo del compilador.
    """
    return {"status": "not_implemented", "input": source}
