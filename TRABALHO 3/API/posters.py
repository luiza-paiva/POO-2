import os
import re
import unicodedata
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from db import pg

router = APIRouter(prefix="/posters", tags=["posters"])

PASTA_POSTERS = Path(os.environ.get("PASTA_POSTERS", Path(__file__).resolve().parent / "posters"))
EXTENSOES = (".jpg", ".jpeg", ".png", ".webp")


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