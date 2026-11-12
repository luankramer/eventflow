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


def tipo_real(conteudo: bytes) -> str | None:
    """Descobre o formato pelos primeiros bytes do arquivo (a "assinatura"), sem confiar
    no tipo que o celular informou. Um HTML ou script renomeado para .png é recusado."""
    if conteudo.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if conteudo.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if conteudo[:4] == b"RIFF" and conteudo[8:12] == b"WEBP":
        return "image/webp"
    if conteudo[4:8] == b"ftyp" and conteudo[8:12] in (b"heic", b"heix", b"hevc", b"heim", b"heis", b"mif1", b"msf1"):
        return "image/heif" if conteudo[8:12] in (b"mif1", b"msf1") else "image/heic"
    return None


async def _ler_com_limite(arquivo: UploadFile, limite: int) -> bytes:
    """Lê em pedaços e para assim que passar do limite, sem carregar o arquivo inteiro."""
    partes, total = [], 0
    while pedaco := await arquivo.read(256 * 1024):
        total += len(pedaco)
        if total > limite:
            raise HTTPException(413, f"Imagem maior que {config.UPLOAD_MAX_MB} MB.")
        partes.append(pedaco)
    return b"".join(partes)


async def salvar_imagem(arquivo: UploadFile, base_url: str, db: Session) -> str:
    if (arquivo.content_type or "").lower() not in EXTENSOES:
        raise HTTPException(400, "Envie uma imagem JPG, PNG, WEBP ou HEIC.")

    conteudo = await _ler_com_limite(arquivo, config.UPLOAD_MAX_MB * 1024 * 1024)
    if not conteudo:
        raise HTTPException(400, "Arquivo vazio.")
    tipo = tipo_real(conteudo)
    if tipo is None:
        raise HTTPException(400, "O arquivo não é uma imagem válida.")

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
