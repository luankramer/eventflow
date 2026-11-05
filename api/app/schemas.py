from datetime import date, time

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


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


class LoginIn(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


# ---------- Categoria ----------
class CategoriaIn(BaseModel):
    nome: str = Field(min_length=2, max_length=80)
    descricao: str | None = None

    @field_validator("nome")
    @classmethod
    def limpar(cls, v: str) -> str:
        return v.strip()


class CategoriaOut(Orm):
    id: int
    nome: str
    descricao: str | None = None


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
    descricao: str | None = None
    data: date
    hora: time
    preco: float = Field(ge=0)
    categoria_id: int
    local_id: int
    imagem_url: str | None = Field(default=None, max_length=500)


class EventoOut(Orm):
    id: int
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
