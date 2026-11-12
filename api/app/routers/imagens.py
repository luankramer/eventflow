import re

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi import Path as ParametroCaminho
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Imagem

FORMATO_ID = re.compile(r"[0-9a-f]{32}")

router = APIRouter(tags=["Upload"])


@router.get("/imagens/{nome}")
def ver_imagem(nome: str = ParametroCaminho(max_length=60), db: Session = Depends(get_db)):
    """Serve a foto do evento. É pública (sem token) para o app exibir com <img>.
    O nome é aleatório (uuid), então não dá para adivinhar imagens."""
    # Só aceita o formato que a própria API gera: 32 letras/números hexadecimais + extensão.
    id_imagem = nome.split(".")[0]
    imagem = db.get(Imagem, id_imagem) if FORMATO_ID.fullmatch(id_imagem) else None
    if imagem is None:
        raise HTTPException(404, "Imagem não encontrada.")
    return Response(
        content=imagem.conteudo,
        media_type=imagem.tipo,
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "Content-Disposition": "inline",
            "Content-Security-Policy": "default-src 'none'; sandbox",
        },
    )
