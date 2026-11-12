from datetime import date, time
from typing import Annotated

from fastapi import Path as ParametroCaminho

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


# Maior inteiro que o Postgres guarda numa coluna INTEGER.
ID_MAXIMO = 2_147_483_647
# Id vindo na URL: positivo e dentro do limite (evita erro 500 com números gigantes).
Id = Annotated[int, ParametroCaminho(ge=1, le=ID_MAXIMO)]


class Orm(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Usuário / Auth ----------
class UsuarioOut(Orm):
    id: int
    nome: str
    email: EmailStr


class RegistroIn(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    email: EmailStr
    senha: str = Field(min_length=6, max_length=72)

    @field_validator("senha")
    @classmethod
    def limite_bcrypt(cls, v: str) -> str:
        # O bcrypt só aceita até 72 bytes; letras com acento ocupam 2 bytes.
        if len(v.encode("utf-8")) > 72:
            raise ValueError("A senha pode ter no máximo 72 bytes (menos caracteres se tiver acentos).")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=200)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


# ---------- Categoria ----------
class CategoriaIn(BaseModel):
    nome: str = Field(min_length=2, max_length=80)
    descricao: str | None = Field(default=None, max_length=500)
    cor: str | None = Field(default=None, pattern=r"^#[0-9A-Fa-f]{6}$", description="Cor em hexadecimal, ex.: #E8175D")
    icone: str | None = Field(default=None, pattern=r"^[a-z0-9-]{1,40}$", description="Nome do ícone, ex.: musica")

    @field_validator("nome")
    @classmethod
    def limpar(cls, v: str) -> str:
        return v.strip()

    @field_validator("cor")
    @classmethod
    def maiusculas(cls, v: str | None) -> str | None:
        return v.upper() if v else v


class CategoriaOut(Orm):
    id: int
    nome: str
    descricao: str | None = None
    cor: str | None = None
    icone: str | None = None


# ---------- Local ----------
class LocalIn(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    endereco: str | None = Field(default=None, max_length=255)


class LocalOut(Orm):
    id: int
    nome: str
    latitude: float
    longitude: float
    endereco: str | None = None


# ---------- Evento ----------
class EventoIn(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    descricao: str | None = Field(default=None, max_length=5000)
    data: date
    hora: time
    preco: float = Field(ge=0, le=1_000_000)
    categoria_id: int = Field(gt=0, le=ID_MAXIMO)
    local_id: int = Field(gt=0, le=ID_MAXIMO)
    imagem_url: str | None = Field(default=None, max_length=500, pattern=r"^https?://")


class EventoOut(Orm):
    id: int
    criado_por_id: int | None = None
    nome: str
    descricao: str | None = None
    data: date
    hora: time
    preco: float
    imagem_url: str | None = None
    categoria: CategoriaOut
    local: LocalOut


class UploadOut(BaseModel):
    url: str
