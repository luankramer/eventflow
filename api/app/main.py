import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, inspect, select, text

from . import config
from .database import Base, SessionLocal, engine
from .models import Usuario
from .moderacao import popular_palavras_padrao
from .routers import admin, auth, categorias, eventos, imagens, locais
from .security import gerar_hash, verificar_senha


log = logging.getLogger("eventflow")


# Colunas que surgiram depois da primeira versão do banco (tabela, coluna, tipo SQL).
COLUNAS_NOVAS = [
    ("categorias", "cor", "varchar(7)"),
    ("categorias", "icone", "varchar(40)"),
    ("usuarios", "admin", "boolean NOT NULL DEFAULT false"),
    ("usuarios", "bloqueado", "boolean NOT NULL DEFAULT false"),
    ("eventos", "oculto", "boolean NOT NULL DEFAULT false"),
]


def _atualizar_esquema() -> None:
    """Bancos criados por versões antigas ganham as colunas novas (sem apagar dados)."""
    existentes = inspect(engine)
    with engine.begin() as conn:
        for tabela, coluna, tipo in COLUNAS_NOVAS:
            if coluna not in {c["name"] for c in existentes.get_columns(tabela)}:
                conn.execute(text(f"ALTER TABLE {tabela} ADD COLUMN {coluna} {tipo}"))


def _garantir_admin() -> None:
    """Cria (ou atualiza) a conta de administrador a partir de ADMIN_EMAIL e ADMIN_SENHA."""
    if not config.ADMIN_SENHA:
        log.warning("ADMIN_SENHA não definida: a área de administração fica sem conta ADM.")
        return
    if len(config.ADMIN_SENHA) < 8 or len(config.ADMIN_SENHA.encode("utf-8")) > 72:
        raise RuntimeError("ADMIN_SENHA precisa ter de 8 a 72 caracteres.")
    with SessionLocal() as db:
        admin = db.scalar(select(Usuario).where(func.lower(Usuario.email) == config.ADMIN_EMAIL))
        if admin is None:
            admin = Usuario(nome="Administrador", email=config.ADMIN_EMAIL, senha_hash=gerar_hash(config.ADMIN_SENHA))
            db.add(admin)
        elif not verificar_senha(config.ADMIN_SENHA, admin.senha_hash):
            admin.senha_hash = gerar_hash(config.ADMIN_SENHA)  # trocou a senha no Render
        admin.admin, admin.bloqueado = True, False
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if config.chave_jwt_insegura(config.DATABASE_URL, config.JWT_SECRET):
        raise RuntimeError("Defina JWT_SECRET com uma chave própria de 32+ caracteres antes de subir em produção.")
    Base.metadata.create_all(bind=engine)  # cria as tabelas na primeira execução
    _atualizar_esquema()
    _garantir_admin()
    with SessionLocal() as db:
        popular_palavras_padrao(db)
    if os.getenv("SEED_DEMO", "").lower() in ("1", "true", "sim"):
        from .dados_exemplo import popular

        popular()
        log.info("Dados de exemplo conferidos (SEED_DEMO).")
    yield


app = FastAPI(
    title="EventFlow API",
    description="API do aplicativo EventFlow — autenticação, eventos, categorias, locais, upload de imagens e moderação (ADM).",
    version="1.3.0",
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
app.include_router(admin.router)

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
