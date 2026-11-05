from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from . import config
from .database import Base, SessionLocal, engine
from .routers import auth, categorias, eventos, locais


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)  # cria as tabelas na primeira execução
    yield


app = FastAPI(
    title="EventFlow API",
    description="API do aplicativo EventFlow — autenticação, eventos, categorias, locais e upload de imagens.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(categorias.router)
app.include_router(locais.router)
app.include_router(eventos.router)

if not config.usa_supabase_storage():
    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=config.UPLOAD_DIR), name="uploads")


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
