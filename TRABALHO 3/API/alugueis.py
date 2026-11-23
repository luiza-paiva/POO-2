import logging

from fastapi import APIRouter, HTTPException
from psycopg.errors import UniqueViolation
from pydantic import BaseModel

from db import driver, pg

log = logging.getLogger("locadora")

router = APIRouter(prefix="/alugueis", tags=["alugueis"])


class AluguelEntrada(BaseModel):
    login: str
    filme_id: str


def _replicar_aluguel(login: str, filme_id: str, titulo: str) -> None:
    try:
        with driver.session() as sessao:
            sessao.run(
                """
                MERGE (u:Usuario {login: $login})
                MERGE (f:Filme {id: $id})
                SET f.titulo = $titulo
                MERGE (u)-[:ALUGOU]->(f)
                """,
                login=login, id=filme_id, titulo=titulo,
            )
    except Exception:
        log.warning("Neo4j indisponível ao replicar aluguel de %s", login)

@router.post("", status_code=201)
def alugar(a: AluguelEntrada):
    with pg() as conn:
        filme = conn.execute(
            "SELECT titulo, copias FROM filmes WHERE id = %s FOR UPDATE",
            (a.filme_id,),
        ).fetchone()
        if not filme:
            raise HTTPException(status_code=404, detail="Filme não encontrado")
        usuario = conn.execute(
            "SELECT 1 FROM usuarios WHERE login = %s", (a.login,)
        ).fetchone()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        ja_tem = conn.execute(
            "SELECT 1 FROM alugueis "
            "WHERE usuario = %s AND filme_id = %s AND data_devolucao IS NULL",
            (a.login, a.filme_id),
        ).fetchone()
        if ja_tem:
            raise HTTPException(status_code=409, detail="Você já alugou este filme")
        ativos = conn.execute(
            "SELECT COUNT(*) FROM alugueis "
            "WHERE filme_id = %s AND data_devolucao IS NULL",
            (a.filme_id,),
        ).fetchone()[0]
        if ativos >= filme[1]:
            raise HTTPException(status_code=409, detail="Não há cópias disponíveis")
        try:
            conn.execute(
                "INSERT INTO alugueis (usuario, filme_id, filme_titulo) "
                "VALUES (%s, %s, %s)",
                (a.login, a.filme_id, filme[0]),
            )
        except UniqueViolation:
            raise HTTPException(status_code=409, detail="Você já alugou este filme")
    _replicar_aluguel(a.login, a.filme_id, filme[0])
    return {"filme": filme[0], "usuario": a.login}


@router.post("/devolucao")
def devolver(a: AluguelEntrada):
    with pg() as conn:
        ativo = conn.execute(
            "SELECT id, filme_titulo FROM alugueis "
            "WHERE filme_id = %s AND usuario = %s AND data_devolucao IS NULL "
            "FOR UPDATE",
            (a.filme_id, a.login),
        ).fetchone()
        if not ativo:
            raise HTTPException(status_code=409, detail="Você não alugou este filme")
        conn.execute(
            "UPDATE alugueis SET data_devolucao = NOW() WHERE id = %s", (ativo[0],)
        )
    return {"filme": ativo[1], "usuario": a.login}


@router.get("/historico")
def historico(usuario: str | None = None):
    filtro = "AND usuario = %(u)s" if usuario else ""
    with pg() as conn:
        linhas = conn.execute(
            f"""
            SELECT data_aluguel AS quando, usuario, filme_titulo, 'Aluguel' AS acao
            FROM alugueis WHERE TRUE {filtro}
            UNION ALL
            SELECT data_devolucao, usuario, filme_titulo, 'Devolução'
            FROM alugueis WHERE data_devolucao IS NOT NULL {filtro}
            ORDER BY quando DESC
            """,
            {"u": usuario},
        ).fetchall()
    return [
        {
            "data_hora": l[0].strftime("%d/%m/%Y %H:%M:%S"),
            "usuario": l[1],
            "filme": l[2],
            "acao": l[3],
        }
        for l in linhas
    ]