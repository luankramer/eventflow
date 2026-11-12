from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Categoria, Evento
from ..schemas import Id, CategoriaIn, CategoriaOut
from ..security import usuario_atual

router = APIRouter(prefix="/categorias", tags=["Categorias"])


def _buscar(db: Session, categoria_id: int) -> Categoria:
    categoria = db.get(Categoria, categoria_id)
    if categoria is None:
        raise HTTPException(404, "Categoria não encontrada.")
    return categoria


def _checar_nome_unico(db: Session, nome: str, ignorar_id: int | None = None) -> None:
    consulta = select(Categoria).where(func.lower(Categoria.nome) == nome.lower())
    if ignorar_id is not None:
        consulta = consulta.where(Categoria.id != ignorar_id)
    if db.scalar(consulta):
        raise HTTPException(409, "Já existe uma categoria com este nome.")


@router.get("", response_model=list[CategoriaOut])
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(Categoria).order_by(Categoria.nome)).all()


@router.get("/{categoria_id}", response_model=CategoriaOut)
def detalhar(categoria_id: Id, db: Session = Depends(get_db)):
    return _buscar(db, categoria_id)


@router.post("", response_model=CategoriaOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(usuario_atual)])
def criar(dados: CategoriaIn, db: Session = Depends(get_db)):
    _checar_nome_unico(db, dados.nome)
    categoria = Categoria(**dados.model_dump())
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.put("/{categoria_id}", response_model=CategoriaOut, dependencies=[Depends(usuario_atual)])
def editar(categoria_id: Id, dados: CategoriaIn, db: Session = Depends(get_db)):
    categoria = _buscar(db, categoria_id)
    _checar_nome_unico(db, dados.nome, ignorar_id=categoria_id)
    for campo, valor in dados.model_dump().items():
        setattr(categoria, campo, valor)
    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(usuario_atual)])
def excluir(categoria_id: Id, db: Session = Depends(get_db)):
    categoria = _buscar(db, categoria_id)
    if db.scalar(select(func.count()).select_from(Evento).where(Evento.categoria_id == categoria_id)):
        raise HTTPException(409, "Não é possível excluir: existem eventos nesta categoria.")
    db.delete(categoria)
    db.commit()
