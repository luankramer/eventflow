"""Configurações lidas de variáveis de ambiente (ou do arquivo .env)."""
import os
from pathlib import Path


def _carregar_env() -> None:
    """Carrega um .env simples (CHAVE=valor) sem depender de bibliotecas extras."""
    arquivo = Path(__file__).resolve().parent.parent / ".env"
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


_carregar_env()


def _normalizar_url_banco(url: str) -> str:
    """O Supabase entrega 'postgresql://...'; o SQLAlchemy precisa do driver psycopg."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


DATABASE_URL = _normalizar_url_banco(os.getenv("DATABASE_URL", "sqlite:///./eventflow.db"))

JWT_SECRET = os.getenv("JWT_SECRET", "chave-de-desenvolvimento-troque-em-producao")
JWT_ALGORITHM = "HS256"
JWT_EXPIRA_DIAS = int(os.getenv("JWT_EXPIRA_DIAS", "30"))

# Supabase Storage (imagens). Se não estiver configurado, salva em disco local (só para desenvolvimento).
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "eventos")

UPLOAD_MAX_MB = int(os.getenv("UPLOAD_MAX_MB", "5"))

# URL pública da API, usada para montar links de imagens salvas localmente.
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")


def usa_supabase_storage() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)
