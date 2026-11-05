from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .config import JWT_ALGORITHM, JWT_EXPIRA_DIAS, JWT_SECRET
from .database import get_db
from .models import Usuario

bearer = HTTPBearer(auto_error=False)


def gerar_hash(senha: str) -> str:
    return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except ValueError:
        return False


def criar_token(usuario_id: int) -> str:
    expira = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRA_DIAS)
    return jwt.encode({"sub": str(usuario_id), "exp": expira}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def usuario_atual(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    erro = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão inválida ou expirada. Faça login novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if cred is None:
        raise erro
    try:
        payload = jwt.decode(cred.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise erro
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise erro
    return usuario
