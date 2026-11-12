"""Armazenamento das imagens dos eventos.

Padrão: a imagem é gravada no próprio banco (tabela `imagens`) e servida pela API em
`/imagens/{nome}`. Assim não depende de chave extra nem do disco do servidor, que no
Render é apagado a cada deploy.

Opcional: com SUPABASE_URL e SUPABASE_SERVICE_KEY configurados, as imagens vão para o
Supabase Storage (bucket SUPABASE_BUCKET).
"""
import uuid

import httpx
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from . import config
from .models import Imagem

EXTENSOES = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
    "image/heif": "heif",
}


async def salvar_imagem(arquivo: UploadFile, base_url: str, db: Session) -> str:
    tipo = (arquivo.content_type or "").lower()
    if tipo not in EXTENSOES:
        raise HTTPException(400, "Envie uma imagem JPG, PNG, WEBP ou HEIC.")

    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(400, "Arquivo vazio.")
    if len(conteudo) > config.UPLOAD_MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"Imagem maior que {config.UPLOAD_MAX_MB} MB.")

    id_imagem = uuid.uuid4().hex
    nome = f"{id_imagem}.{EXTENSOES[tipo]}"

    if config.usa_supabase_storage():
        destino = f"{config.SUPABASE_URL}/storage/v1/object/{config.SUPABASE_BUCKET}/{nome}"
        headers = {"apikey": config.SUPABASE_SERVICE_KEY, "Content-Type": tipo, "x-upsert": "false"}
        # Chave antiga (service_role, um JWT) vai também no Authorization.
        # As chaves novas "sb_secret_..." não são JWT e vão só no header apikey.
        if not config.SUPABASE_SERVICE_KEY.startswith("sb_"):
            headers["Authorization"] = f"Bearer {config.SUPABASE_SERVICE_KEY}"
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(destino, content=conteudo, headers=headers)
        if resp.status_code >= 300:
            raise HTTPException(502, f"Falha ao enviar imagem ao Supabase: {resp.text[:200]}")
        return f"{config.SUPABASE_URL}/storage/v1/object/public/{config.SUPABASE_BUCKET}/{nome}"

    db.add(Imagem(id=id_imagem, tipo=tipo, tamanho=len(conteudo), conteudo=conteudo))
    db.commit()
    raiz = config.PUBLIC_BASE_URL or base_url.rstrip("/")
    return f"{raiz}/imagens/{nome}"
