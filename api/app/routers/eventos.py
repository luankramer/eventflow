from decimal import Decimal

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Categoria, Evento, Local, Usuario
from ..schemas import EventoIn, EventoOut, UploadOut
from ..security import usuario_atual
from ..storage import salvar_imagem

router = APIRouter(tags=["Eventos"], dependencies=[Depends(usuario_atual)])


def _buscar(db: Session, evento_id: int) -> Evento:
    evento = db.get(Evento, evento_id)
    if evento is None:
        raise HTTPException(404, "Evento não encontrado.")
    return evento


def _validar_relacoes(db: Session, dados: EventoIn) -> None:
    if db.get(Categoria, dados.categoria_id) is None:
        raise HTTPException(400, "Categoria informada não existe.")
    if db.get(Local, dados.local_id) is None:
        raise HTTPException(400, "Local informado não existe.")


def _aplicar(evento: Evento, dados: EventoIn) -> None:
    valores = dados.model_dump()
    valores["preco"] = Decimal(str(round(dados.preco, 2)))
    for campo, valor in valores.items():
        setattr(evento, campo, valor)


@router.get("/eventos", response_model=list[EventoOut])
def listar(
    busca: str | None = Query(None, description="Busca por nome, descrição, categoria ou local"),
    categoria_id: int | None = None,
    local_id: int | None = None,
    db: Session = Depends(get_db),
):
    consulta = select(Evento)
    if busca and busca.strip():
        termo = f"%{busca.strip()}%"
        consulta = consulta.where(
            or_(
                Evento.nome.ilike(termo),
                Evento.descricao.ilike(termo),
                Evento.categoria.has(Categoria.nome.ilike(termo)),
                Evento.local.has(Local.nome.ilike(termo)),
            )
        )
    if categoria_id is not None:
        consulta = consulta.where(Evento.categoria_id == categoria_id)
    if local_id is not None:
        consulta = consulta.where(Evento.local_id == local_id)
    consulta = consulta.order_by(Evento.data, Evento.hora, Evento.id)
    return db.scalars(consulta).unique().all()


@router.get("/eventos/{evento_id}", response_model=EventoOut)
def detalhar(evento_id: int, db: Session = Depends(get_db)):
    return _buscar(db, evento_id)


@router.post("/eventos", response_model=EventoOut, status_code=status.HTTP_201_CREATED)
def criar(dados: EventoIn, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    _validar_relacoes(db, dados)
    evento = Evento(criado_por_id=usuario.id)
    _aplicar(evento, dados)
    db.add(evento)
    db.commit()
    return _buscar(db, evento.id)


@router.put("/eventos/{evento_id}", response_model=EventoOut)
def editar(evento_id: int, dados: EventoIn, db: Session = Depends(get_db)):
    evento = _buscar(db, evento_id)
    _validar_relacoes(db, dados)
    _aplicar(evento, dados)
    db.commit()
    db.expire(evento)
    return _buscar(db, evento_id)


@router.delete("/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(evento_id: int, db: Session = Depends(get_db)):
    db.delete(_buscar(db, evento_id))
    db.commit()


@router.post("/upload", response_model=UploadOut, tags=["Upload"])
async def upload_imagem(request: Request, arquivo: UploadFile = File(...)):
    """Recebe a foto (câmera ou galeria) e devolve a URL pública para usar em `imagem_url`."""
    url = await salvar_imagem(arquivo, str(request.base_url))
    return UploadOut(url=url)
