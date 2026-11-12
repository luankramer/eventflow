from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Imagem

router = APIRouter(tags=["Upload"])


@router.get("/imagens/{nome}")
def ver_imagem(nome: str, db: Session = Depends(get_db)):
    """Serve a foto do evento. É pública (sem token) para o app exibir com <img>.
    O nome é aleatório (uuid), então não dá para adivinhar imagens."""
    imagem = db.get(Imagem, nome.split(".")[0])
    if imagem is None:
        raise HTTPException(404, "Imagem não encontrada.")
    return Response(
        content=imagem.conteudo,
        media_type=imagem.tipo,
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
