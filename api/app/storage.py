"""Armazenamento das imagens dos eventos.

Em produção usa o Supabase Storage (o disco do Render é apagado a cada deploy).
Sem Supabase configurado, salva na pasta local `uploads/` (útil só para testar no PC).
"""
import uuid

import httpx
from fastapi import HTTPException, UploadFile

from . import config

EXTENSOES = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
    "image/heif": "heif",
}


async def salvar_imagem(arquivo: UploadFile, base_url: str) -> str:
    tipo = (arquivo.content_type or "").lower()
    if tipo not in EXTENSOES:
        raise HTTPException(400, "Envie uma imagem JPG, PNG, WEBP ou HEIC.")

    conteudo = await arquivo.read()
    if not conteudo:
        raise HTTPException(400, "Arquivo vazio.")
    if len(conteudo) > config.UPLOAD_MAX_MB * 1024 * 1024:
        raise HTTPException(413, f"Imagem maior que {config.UPLOAD_MAX_MB} MB.")

    nome = f"{uuid.uuid4().hex}.{EXTENSOES[tipo]}"

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

    config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (config.UPLOAD_DIR / nome).write_bytes(conteudo)
    raiz = config.PUBLIC_BASE_URL or base_url.rstrip("/")
    return f"{raiz}/uploads/{nome}"
