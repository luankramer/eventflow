"""Regras das diretrizes do EventFlow: o que marca um evento para revisão do ADM.

Um evento fica "fora das diretrizes" quando tem pelo menos um destes problemas:
- palavras: o nome ou a descrição contém um termo da lista de palavras proibidas;
- denuncias: algum usuário denunciou o evento;
- incompleto: falta imagem ou a descrição está vazia ou curta demais.
"""
import re
import unicodedata

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Evento, PalavraProibida
from .schemas import Problema

DESCRICAO_MINIMA = 20

PALAVRAS_PADRAO = [
    "golpe", "pix antecipado", "pirâmide financeira", "dinheiro fácil", "ganhe dinheiro",
    "cassino", "aposta", "arma", "droga", "drogas",
    "porra", "caralho", "merda", "puta", "otário", "idiota",
]


def normalizar(texto: str) -> str:
    """Minúsculas e sem acento, para "Pirâmide" e "piramide" serem iguais."""
    sem_acento = unicodedata.normalize("NFKD", texto or "").encode("ascii", "ignore").decode("ascii")
    return " ".join(sem_acento.lower().split())


def termos_encontrados(texto: str, termos: list[str]) -> list[str]:
    alvo = normalizar(texto)
    achados = []
    for termo in termos:
        # palavra inteira: "arma" não marca "armazém"
        if re.search(rf"(?<![a-z0-9]){re.escape(normalizar(termo))}(?![a-z0-9])", alvo):
            achados.append(termo)
    return achados


def carregar_termos(db: Session) -> list[str]:
    return list(db.scalars(select(PalavraProibida.termo).order_by(PalavraProibida.termo)))


def problemas_do_evento(evento: Evento, termos: list[str], total_denuncias: int) -> list[Problema]:
    problemas = []
    achados = termos_encontrados(f"{evento.nome} {evento.descricao or ''}", termos)
    if achados:
        problemas.append(Problema(tipo="palavras", detalhe="Palavras proibidas: " + ", ".join(achados)))
    if total_denuncias:
        problemas.append(Problema(tipo="denuncias", detalhe=f"{total_denuncias} denúncia(s) de usuários"))
    faltando = []
    if not evento.imagem_url:
        faltando.append("sem imagem")
    if len((evento.descricao or "").strip()) < DESCRICAO_MINIMA:
        faltando.append("descrição vazia ou curta")
    if faltando:
        problemas.append(Problema(tipo="incompleto", detalhe="Cadastro incompleto: " + ", ".join(faltando)))
    return problemas


def popular_palavras_padrao(db: Session) -> None:
    """Na primeira vez, cria a lista inicial de palavras proibidas."""
    if db.scalar(select(PalavraProibida.id).limit(1)) is None:
        db.add_all(PalavraProibida(termo=t) for t in PALAVRAS_PADRAO)
        db.commit()
