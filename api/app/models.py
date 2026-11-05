from datetime import date, datetime, time, timezone
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def agora() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(200))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(80), unique=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    cor: Mapped[str | None] = mapped_column(String(7), nullable=True)  # ex.: "#E8175D"
    icone: Mapped[str | None] = mapped_column(String(40), nullable=True)  # ex.: "musica"

    eventos: Mapped[list["Evento"]] = relationship(back_populates="categoria")


class Local(Base):
    __tablename__ = "locais"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120))
    latitude: Mapped[float]
    longitude: Mapped[float]
    endereco: Mapped[str | None] = mapped_column(String(255), nullable=True)

    eventos: Mapped[list["Evento"]] = relationship(back_populates="local")


class Evento(Base):
    __tablename__ = "eventos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(150))
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    data: Mapped[date] = mapped_column(Date)
    hora: Mapped[time] = mapped_column(Time)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    imagem_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"))
    local_id: Mapped[int] = mapped_column(ForeignKey("locais.id"))
    criado_por_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)

    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora, onupdate=agora)

    categoria: Mapped[Categoria] = relationship(back_populates="eventos", lazy="joined")
    local: Mapped[Local] = relationship(back_populates="eventos", lazy="joined")
