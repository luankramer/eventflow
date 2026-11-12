import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from . import config
from .database import Base, SessionLocal, engine
from .routers import auth, categorias, eventos, imagens, locais


log = logging.getLogger("eventflow")


def _atualizar_esquema() -> None:
    """Bancos criados antes da cor/ícone nas categorias ganham as colunas novas."""
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        conn.execute(text(
            "ALTER TABLE categorias ADD COLUMN IF NOT EXISTS cor varchar(7), "
            "ADD COLUMN IF NOT EXISTS icone varchar(40)"
        ))


@asynccontextmanager
async def lifespan(_: FastAPI):
    if config.chave_jwt_insegura(config.DATABASE_URL, config.JWT_SECRET):
        raise RuntimeError("Defina JWT_SECRET com uma chave própria de 32+ caracteres antes de subir em produção.")
    Base.metadata.create_all(bind=engine)  # cria as tabelas na primeira execução
    _atualizar_esquema()
    if os.getenv("SEED_DEMO", "").lower() in ("1", "true", "sim"):
        from .dados_exemplo import popular

        popular()
        log.info("Dados de exemplo conferidos (SEED_DEMO).")
    yield


app = FastAPI(
    title="EventFlow API",
    description="API do aplicativo EventFlow — autenticação, eventos, categorias, locais e upload de imagens.",
    version="1.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # O app autentica com token no cabeçalho (sem cookies), então liberar a origem não
    # expõe sessão de ninguém. Métodos e cabeçalhos ficam só nos que o app usa.
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

CABECALHOS_SEGURANCA = {
    "X-Content-Type-Options": "nosniff",   # o navegador não "adivinha" o tipo do arquivo
    "X-Frame-Options": "DENY",             # a API não pode ser embutida em outro site
    "Referrer-Policy": "no-referrer",
    "Strict-Transport-Security": "max-age=31536000",
}


@app.middleware("http")
async def cabecalhos_de_seguranca(request: Request, call_next):
    resposta = await call_next(request)
    for chave, valor in CABECALHOS_SEGURANCA.items():
        resposta.headers.setdefault(chave, valor)
    return resposta


app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(locais.router)
app.include_router(eventos.router)
app.include_router(imagens.router)

@app.get("/", tags=["Status"])
def raiz():
    return {"app": "EventFlow API", "docs": "/docs", "status": "online"}


@app.get("/health", tags=["Status"])
def health():
    """Usada pelo cron-job.org para manter a API e o banco acordados."""
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception as erro:  # noqa: BLE001
        raise HTTPException(503, f"Banco indisponível: {type(erro).__name__}")
    return {"status": "ok", "banco": "ok"}
