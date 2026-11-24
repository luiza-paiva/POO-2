import os
import re
import unicodedata
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from db import pg

router = APIRouter(prefix="/posters", tags=["posters"])

PASTA_POSTERS = Path(os.environ.get("PASTA_POSTERS", Path(__file__).resolve().parent / "posters"))
EXTENSOES = (".jpg", ".jpeg", ".png", ".webp")

TIPOS = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
LIMITE_BYTES = 5 * 1024 * 1024


def renomear_poster(titulo_antigo: str, titulo_novo: str) -> None:
    """Mantém o pôster quando o título do filme muda."""
    antigo, novo = _nome_arquivo(titulo_antigo), _nome_arquivo(titulo_novo)
    if antigo == novo:
        return
    for ext in EXTENSOES:
        origem = PASTA_POSTERS / (antigo + ext)
        if origem.is_file():
            origem.replace(PASTA_POSTERS / (novo + ext))
            break


@router.put("/{filme_id}", status_code=204)
async def enviar(filme_id: str, request: Request):
    tipo = request.headers.get("content-type", "").split(";")[0]
    if tipo not in TIPOS:
        raise HTTPException(status_code=415, detail="Use uma imagem JPG, PNG ou WEBP")
    dados = await request.body()
    if not dados or len(dados) > LIMITE_BYTES:
        raise HTTPException(status_code=422, detail="A imagem deve ter até 5 MB")
    with pg() as conn:
        linha = conn.execute("SELECT titulo FROM filmes WHERE id = %s", (filme_id,)).fetchone()
    if not linha:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    base = _nome_arquivo(linha[0])
    PASTA_POSTERS.mkdir(parents=True, exist_ok=True)
    for ext in EXTENSOES:
        antigo = PASTA_POSTERS / (base + ext)
        if antigo.is_file():
            antigo.unlink()
    (PASTA_POSTERS / (base + TIPOS[tipo])).write_bytes(dados)


def _nome_arquivo(titulo: str) -> str:
    texto = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


@router.get("/{filme_id}")
def poster(filme_id: str):
    with pg() as conn:
        linha = conn.execute("SELECT titulo FROM filmes WHERE id = %s", (filme_id,)).fetchone()
    if not linha:
        raise HTTPException(status_code=404, detail="Filme não encontrado")
    base = _nome_arquivo(linha[0])
    for ext in EXTENSOES:
        caminho = PASTA_POSTERS / (base + ext)
        if caminho.is_file():
            return FileResponse(caminho)
    raise HTTPException(status_code=404, detail="Filme sem pôster")