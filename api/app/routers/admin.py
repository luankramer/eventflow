"""Área do administrador: moderação de eventos, denúncias, palavras proibidas e usuários.
Todas as rotas exigem a conta de ADM (403 para os demais)."""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Denuncia, Evento, PalavraProibida, Usuario
from ..moderacao import carregar_termos, normalizar, problemas_do_evento
from ..schemas import (
    BloqueioIn, DenunciaOut, EventoAdminOut, Id, OcultarIn, PalavraIn, PalavraOut, ResumoAdmin, UsuarioAdminOut,
)
from ..security import exigir_admin

router = APIRouter(prefix="/admin", tags=["Administração"], dependencies=[Depends(exigir_admin)])

Filtro = Literal["fora", "palavras", "denuncias", "incompletos", "ocultos", "todos"]


def _avaliar(db: Session) -> list[EventoAdminOut]:
    """Todos os eventos (inclusive ocultos) com os problemas de diretriz de cada um."""
    termos = carregar_termos(db)
    contagem = dict(db.execute(select(Denuncia.evento_id, func.count()).group_by(Denuncia.evento_id)).all())
    saida = []
    for evento in db.scalars(select(Evento).order_by(Evento.data, Evento.id)).unique():
        total = contagem.get(evento.id, 0)
        item = EventoAdminOut.model_validate(evento)
        item.total_denuncias = total
        item.problemas = problemas_do_evento(evento, termos, total)
        saida.append(item)
    return saida


def _evento(db: Session, evento_id: int) -> Evento:
    evento = db.get(Evento, evento_id)
    if evento is None:
        raise HTTPException(404, "Evento não encontrado.")
    return evento


@router.get("/resumo", response_model=ResumoAdmin)
def resumo(db: Session = Depends(get_db)):
    eventos = _avaliar(db)
    tem = lambda e, tipo: any(p.tipo == tipo for p in e.problemas)  # noqa: E731
    return ResumoAdmin(
        fora_das_diretrizes=sum(1 for e in eventos if e.problemas),
        denunciados=sum(1 for e in eventos if tem(e, "denuncias")),
        com_palavras=sum(1 for e in eventos if tem(e, "palavras")),
        incompletos=sum(1 for e in eventos if tem(e, "incompleto")),
        ocultos=sum(1 for e in eventos if e.oculto),
        usuarios=db.scalar(select(func.count()).select_from(Usuario)),
        usuarios_bloqueados=db.scalar(select(func.count()).select_from(Usuario).where(Usuario.bloqueado.is_(True))),
    )


@router.get("/eventos", response_model=list[EventoAdminOut])
def eventos(
    filtro: Filtro = Query("fora", description="fora = qualquer problema; ou um problema específico; ocultos; todos"),
    busca: str | None = Query(None, max_length=100),
    db: Session = Depends(get_db),
):
    lista = _avaliar(db)
    if filtro == "fora":
        lista = [e for e in lista if e.problemas]
    elif filtro == "ocultos":
        lista = [e for e in lista if e.oculto]
    elif filtro in ("palavras", "denuncias"):
        lista = [e for e in lista if any(p.tipo == filtro for p in e.problemas)]
    elif filtro == "incompletos":
        lista = [e for e in lista if any(p.tipo == "incompleto" for p in e.problemas)]
    if busca and busca.strip():
        termo = normalizar(busca)
        lista = [e for e in lista if termo in normalizar(f"{e.nome} {e.descricao or ''} {e.criado_por.nome if e.criado_por else ''}")]
    # mais denunciados primeiro
    return sorted(lista, key=lambda e: (-e.total_denuncias, -len(e.problemas), e.data))


@router.put("/eventos/{evento_id}/ocultar", response_model=EventoAdminOut)
def ocultar(evento_id: Id, dados: OcultarIn, db: Session = Depends(get_db)):
    """Tira o evento da lista e do mapa públicos (ou devolve), sem apagar nada."""
    evento = _evento(db, evento_id)
    evento.oculto = dados.oculto
    db.commit()
    return next(e for e in _avaliar(db) if e.id == evento_id)


@router.delete("/eventos/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_evento(evento_id: Id, db: Session = Depends(get_db)):
    db.delete(_evento(db, evento_id))
    db.commit()


@router.get("/eventos/{evento_id}/denuncias", response_model=list[DenunciaOut])
def denuncias(evento_id: Id, db: Session = Depends(get_db)):
    _evento(db, evento_id)
    return db.scalars(select(Denuncia).where(Denuncia.evento_id == evento_id).order_by(Denuncia.criado_em.desc())).all()


@router.delete("/eventos/{evento_id}/denuncias", status_code=status.HTTP_204_NO_CONTENT)
def descartar_denuncias(evento_id: Id, db: Session = Depends(get_db)):
    """O ADM analisou e o evento está ok: as denúncias são arquivadas (apagadas)."""
    _evento(db, evento_id)
    for d in db.scalars(select(Denuncia).where(Denuncia.evento_id == evento_id)):
        db.delete(d)
    db.commit()


# ---------- Palavras proibidas ----------
@router.get("/palavras", response_model=list[PalavraOut])
def palavras(db: Session = Depends(get_db)):
    return db.scalars(select(PalavraProibida).order_by(PalavraProibida.termo)).all()


@router.post("/palavras", response_model=PalavraOut, status_code=status.HTTP_201_CREATED)
def adicionar_palavra(dados: PalavraIn, db: Session = Depends(get_db)):
    palavra = PalavraProibida(termo=dados.termo)
    db.add(palavra)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Essa palavra já está na lista.")
    db.refresh(palavra)
    return palavra


@router.delete("/palavras/{palavra_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_palavra(palavra_id: Id, db: Session = Depends(get_db)):
    palavra = db.get(PalavraProibida, palavra_id)
    if palavra is None:
        raise HTTPException(404, "Palavra não encontrada.")
    db.delete(palavra)
    db.commit()


# ---------- Usuários ----------
@router.get("/usuarios", response_model=list[UsuarioAdminOut])
def usuarios(db: Session = Depends(get_db)):
    contagem = dict(db.execute(select(Evento.criado_por_id, func.count()).group_by(Evento.criado_por_id)).all())
    saida = []
    for u in db.scalars(select(Usuario).order_by(Usuario.admin.desc(), Usuario.nome)):
        item = UsuarioAdminOut.model_validate(u)
        item.total_eventos = contagem.get(u.id, 0)
        saida.append(item)
    return saida


@router.put("/usuarios/{usuario_id}/bloqueio", response_model=UsuarioAdminOut)
def bloquear(usuario_id: Id, dados: BloqueioIn, db: Session = Depends(get_db)):
    """Usuário bloqueado não entra no app nem cadastra nada; os eventos dele continuam (o ADM decide)."""
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(404, "Usuário não encontrado.")
    if usuario.admin:
        raise HTTPException(400, "A conta de administrador não pode ser bloqueada.")
    usuario.bloqueado = dados.bloqueado
    db.commit()
    item = UsuarioAdminOut.model_validate(usuario)
    item.total_eventos = db.scalar(select(func.count()).select_from(Evento).where(Evento.criado_por_id == usuario.id))
    return item
