from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Usuario
from ..schemas import LoginIn, RegistroIn, TokenOut, UsuarioOut
from ..security import criar_token, gerar_hash, usuario_atual, verificar_senha

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/registro", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def registrar(dados: RegistroIn, db: Session = Depends(get_db)):
    email = dados.email.lower()
    if db.scalar(select(Usuario).where(func.lower(Usuario.email) == email)):
        raise HTTPException(409, "Já existe uma conta com este e-mail.")
    usuario = Usuario(nome=dados.nome.strip(), email=email, senha_hash=gerar_hash(dados.senha))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return TokenOut(access_token=criar_token(usuario.id), usuario=UsuarioOut.model_validate(usuario))


@router.post("/login", response_model=TokenOut)
def login(dados: LoginIn, db: Session = Depends(get_db)):
    usuario = db.scalar(select(Usuario).where(func.lower(Usuario.email) == dados.email.lower()))
    if usuario is None or not verificar_senha(dados.senha, usuario.senha_hash):
        raise HTTPException(401, "E-mail ou senha incorretos.")
    return TokenOut(access_token=criar_token(usuario.id), usuario=UsuarioOut.model_validate(usuario))


@router.get("/me", response_model=UsuarioOut)
def perfil(usuario: Usuario = Depends(usuario_atual)):
    """Dados do usuário logado (tela de Perfil). Também serve para o app validar a sessão salva."""
    return usuario


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(_: Usuario = Depends(usuario_atual)):
    """O JWT não fica guardado no servidor: o logout real é o app apagar o token salvo.
    Esta rota existe para o app chamar antes de limpar a sessão."""
    return None
