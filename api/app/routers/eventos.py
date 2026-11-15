from typing import Literal
from decimal import Decimal

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Categoria, Denuncia, Evento, Local, Usuario, hoje_local
from ..schemas import ID_MAXIMO, DenunciaIn, EventoIn, EventoOut, Id, UploadOut
from ..security import usuario_atual
from ..storage import salvar_imagem

router = APIRouter(tags=["Eventos"])


def _buscar(db: Session, evento_id: int, incluir_oculto: bool = False) -> Evento:
    evento = db.get(Evento, evento_id)
    if evento is None or (evento.oculto and not incluir_oculto):
        raise HTTPException(404, "Evento não encontrado.")
    return evento


def _exigir_dono(evento: Evento, usuario: Usuario, admin_pode: bool = False) -> None:
    """Qualquer pessoa logada cria eventos, mas só quem criou pode editar ou excluir.
    O administrador também pode excluir (moderação)."""
    if evento.criado_por_id != usuario.id and not (admin_pode and usuario.admin):
        raise HTTPException(403, "Só quem cadastrou este evento pode alterá-lo.")


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
    busca: str | None = Query(None, max_length=100, description="Busca por nome, descrição, categoria ou local"),
    categoria_id: int | None = Query(None, gt=0, le=ID_MAXIMO),
    local_id: int | None = Query(None, gt=0, le=ID_MAXIMO),
    periodo: Literal["todos", "proximos", "encerrados"] = Query(
        "todos", description="proximos = de hoje em diante; encerrados = já passaram (o app mostra como Indisponível)"
    ),
    db: Session = Depends(get_db),
):
    consulta = select(Evento).where(Evento.oculto.is_(False))  # ocultos pelo ADM não aparecem
    hoje = hoje_local()
    if periodo == "proximos":
        consulta = consulta.where(Evento.data >= hoje)
    elif periodo == "encerrados":
        consulta = consulta.where(Evento.data < hoje)
    if busca and busca.strip():
        # Parâmetro ligado pelo SQLAlchemy (nunca texto colado no SQL) e com % e _ escapados,
        # para que a busca "50%" procure "50%" e não "qualquer coisa".
        termo = busca.strip()
        consulta = consulta.where(
            or_(
                Evento.nome.icontains(termo, autoescape=True),
                Evento.descricao.icontains(termo, autoescape=True),
                Evento.categoria.has(Categoria.nome.icontains(termo, autoescape=True)),
                Evento.local.has(Local.nome.icontains(termo, autoescape=True)),
            )
        )
    if categoria_id is not None:
        consulta = consulta.where(Evento.categoria_id == categoria_id)
    if local_id is not None:
        consulta = consulta.where(Evento.local_id == local_id)
    if periodo == "encerrados":  # os que acabaram de passar primeiro
        consulta = consulta.order_by(Evento.data.desc(), Evento.hora.desc(), Evento.id)
    else:
        consulta = consulta.order_by(Evento.data, Evento.hora, Evento.id)
    return db.scalars(consulta).unique().all()


@router.get("/eventos/{evento_id}", response_model=EventoOut)
def detalhar(evento_id: Id, db: Session = Depends(get_db)):
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
def editar(evento_id: Id, dados: EventoIn, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    evento = _buscar(db, evento_id)
    _exigir_dono(evento, usuario)
    _validar_relacoes(db, dados)
    _aplicar(evento, dados)
    db.commit()
    db.expire(evento)
    return _buscar(db, evento_id)


@router.delete("/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir(evento_id: Id, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    evento = _buscar(db, evento_id, incluir_oculto=usuario.admin)
    _exigir_dono(evento, usuario, admin_pode=True)
    db.delete(evento)
    db.commit()


@router.post("/eventos/{evento_id}/denuncias", status_code=status.HTTP_201_CREATED, tags=["Denúncias"])
def denunciar(evento_id: Id, dados: DenunciaIn, db: Session = Depends(get_db), usuario: Usuario = Depends(usuario_atual)):
    """Usuário logado avisa o ADM que o evento está fora das diretrizes (uma denúncia por pessoa)."""
    evento = _buscar(db, evento_id)
    if evento.criado_por_id == usuario.id:
        raise HTTPException(400, "Você não pode denunciar o próprio evento.")
    db.add(Denuncia(evento_id=evento.id, usuario_id=usuario.id, motivo=dados.motivo, detalhe=(dados.detalhe or "").strip() or None))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Você já denunciou este evento.")
    return {"mensagem": "Denúncia enviada. O administrador vai analisar."}


@router.post("/upload", response_model=UploadOut, tags=["Upload"], dependencies=[Depends(usuario_atual)])
async def upload_imagem(request: Request, arquivo: UploadFile = File(...), db: Session = Depends(get_db)):
    """Recebe a foto (câmera ou galeria) e devolve a URL pública para usar em `imagem_url`."""
    url = await salvar_imagem(arquivo, str(request.base_url), db)
    return UploadOut(url=url)
