from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Evento, Local
from ..schemas import Id, LocalIn, LocalOut
from ..security import usuario_atual

router = APIRouter(prefix="/locais", tags=["Locais"])


def _buscar(db: Session, local_id: int) -> Local:
    local = db.get(Local, local_id)
    if local is None:
        raise HTTPException(404, "Local não encontrado.")
    return local


@router.get("", response_model=list[LocalOut])
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(Local).order_by(Local.nome)).all()


@router.get("/{local_id}", response_model=LocalOut)
def detalhar(local_id: Id, db: Session = Depends(get_db)):
    return _buscar(db, local_id)


@router.post("", response_model=LocalOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(usuario_atual)])
def criar(dados: LocalIn, db: Session = Depends(get_db)):
    local = Local(**dados.model_dump())
    db.add(local)
    db.commit()
    db.refresh(local)
    return local


@router.put("/{local_id}", response_model=LocalOut, dependencies=[Depends(usuario_atual)])
def editar(local_id: Id, dados: LocalIn, db: Session = Depends(get_db)):
    local = _buscar(db, local_id)
    for campo, valor in dados.model_dump().items():
        setattr(local, campo, valor)
    db.commit()
    db.refresh(local)
    return local


@router.delete("/{local_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(usuario_atual)])
def excluir(local_id: Id, db: Session = Depends(get_db)):
    local = _buscar(db, local_id)
    if db.scalar(select(func.count()).select_from(Evento).where(Evento.local_id == local_id)):
        raise HTTPException(409, "Não é possível excluir: existem eventos neste local.")
    db.delete(local)
    db.commit()
