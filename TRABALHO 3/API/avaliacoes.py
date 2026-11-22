from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db import pg

router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])


class AvaliacaoEntrada(BaseModel):
    login: str
    filme_id: str
    nota: int = Field(ge=1, le=5)
    comentario: str = ""


@router.post("")
def avaliar(a: AvaliacaoEntrada):
    with pg() as conn:
        alugou = conn.execute(
            "SELECT 1 FROM alugueis WHERE usuario = %s AND filme_id = %s",
            (a.login, a.filme_id),
        ).fetchone()
        if not alugou:
            raise HTTPException(
                status_code=403, detail="Você só pode avaliar filmes que já alugou"
            )
        conn.execute(
            """
            INSERT INTO avaliacoes (usuario, filme_id, nota, comentario)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (usuario, filme_id)
            DO UPDATE SET nota = EXCLUDED.nota,
                          comentario = EXCLUDED.comentario,
                          data_hora = NOW()
            """,
            (a.login, a.filme_id, a.nota, a.comentario),
        )
    return {"filme_id": a.filme_id, "usuario": a.login, "nota": a.nota}


@router.get("/{filme_id}")
def listar(filme_id: str):
    with pg() as conn:
        linhas = conn.execute(
            "SELECT usuario, nota, comentario, data_hora FROM avaliacoes "
            "WHERE filme_id = %s ORDER BY data_hora DESC",
            (filme_id,),
        ).fetchall()
    return [
        {
            "usuario": l[0],
            "nota": l[1],
            "comentario": l[2] or "",
            "data_hora": l[3].strftime("%d/%m/%Y %H:%M:%S"),
        }
        for l in linhas
    ]