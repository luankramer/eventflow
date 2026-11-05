from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    # prepare_threshold=None evita erros com o pooler do Supabase (modo transação).
    connect_args = {"prepare_threshold": None}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
