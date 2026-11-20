import logging
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db import driver, pg

log = logging.getLogger("locadora")

router = APIRouter(prefix="/filmes", tags=["filmes"])

GENEROS = ["romance", "ação", "drama", "terror", "ficção científica"]

FILMES_INICIAIS = [
    ("O Poderoso Chefão", "drama"),
    ("Pânico", "terror"),
    ("Duna", "ficção científica"),
    ("Titanic", "romance"),
    ("Interestelar", "ficção científica"),
    ("John Wick", "ação"),
    ("Invocação do Mal", "terror"),
    ("Orgulho e Preconceito", "romance"),
    ("Clube da Luta", "drama"),
    ("Mad Max: Estrada da Fúria", "ação"),
    ("Corra!", "terror"),
    ("Blade Runner 2049", "ficção científica"),
    ("Diário de uma Paixão", "romance"),
    ("Cidade de Deus", "drama"),
    ("Um Sonho de Liberdade", "drama"),
]


class FilmeEntrada(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    genero: str


def _replicar_filme(filme_id: str, titulo: str, genero: str) -> None:
    """Projeta o filme no Neo4j (MERGE: repetir é seguro)."""
    try:
        with driver.session() as sessao:
            sessao.run(
                """
                MERGE (f:Filme {id: $id})
                SET f.titulo = $titulo
                WITH f
                OPTIONAL MATCH (f)-[r:DO_GENERO]->()
                DELETE r
                WITH DISTINCT f
                MERGE (g:Genero {nome: $genero})
                MERGE (f)-[:DO_GENERO]->(g)
                """,
                id=filme_id, titulo=titulo, genero=genero,
            )
    except Exception:
        log.warning("Neo4j indisponível ao replicar filme %s", filme_id)


def _id_genero(conn, nome: str) -> int:
    linha = conn.execute("SELECT id FROM generos WHERE nome = %s", (nome,)).fetchone()
    if not linha:
        raise HTTPException(status_code=422, detail=f"Gênero inválido: {nome}")
    return linha[0]


def _filme_dict(l) -> dict:
    return {
        "id": l[0],
        "titulo": l[1],
        "genero": l[2],
        "status": "Alugado" if l[3] else "Disponível",
        "alugado_por": l[3] or "",
        "data_aluguel": l[4].strftime("%d/%m/%Y %H:%M:%S") if l[4] else "",
        "media": round(float(l[5]), 1),
        "qtd_avaliacoes": int(l[6]),
    }


def semear() -> None:
    """Gêneros fixos e catálogo inicial (só se não houver nenhum filme)."""
    novos = []
    with pg() as conn:
        for g in GENEROS:
            conn.execute(
                "INSERT INTO generos (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING",
                (g,),
            )
        vazio = conn.execute("SELECT NOT EXISTS (SELECT 1 FROM filmes)").fetchone()[0]
        if vazio:
            for titulo, genero in FILMES_INICIAIS:
                fid = uuid.uuid4().hex
                conn.execute(
                    "INSERT INTO filmes (id, titulo, genero_id) "
                    "SELECT %s, %s, id FROM generos WHERE nome = %s",
                    (fid, titulo, genero),
                )
                novos.append((fid, titulo, genero))
    for fid, titulo, genero in novos:
        _replicar_filme(fid, titulo, genero)


@router.get("/generos")
def listar_generos():
    with pg() as conn:
        linhas = conn.execute("SELECT nome FROM generos ORDER BY nome").fetchall()
    return [l[0] for l in linhas]


@router.get("")
def listar():
    with pg() as conn:
        linhas = conn.execute(
            """
            SELECT f.id, f.titulo, g.nome, a.usuario, a.data_aluguel,
                   COALESCE(av.media, 0), COALESCE(av.qtd, 0)
            FROM filmes f
            JOIN generos g ON g.id = f.genero_id
            LEFT JOIN alugueis a ON a.filme_id = f.id AND a.data_devolucao IS NULL
            LEFT JOIN (
                SELECT filme_id, AVG(nota) AS media, COUNT(*) AS qtd
                FROM avaliacoes GROUP BY filme_id
            ) av ON av.filme_id = f.id
            ORDER BY g.nome, f.titulo
            """
        ).fetchall()
    return [_filme_dict(l) for l in linhas]


@router.post("", status_code=201)
def cadastrar(f: FilmeEntrada):
    novo_id = uuid.uuid4().hex
    titulo = f.titulo.strip()
    with pg() as conn:
        genero_id = _id_genero(conn, f.genero)
        conn.execute(
            "INSERT INTO filmes (id, titulo, genero_id) VALUES (%s, %s, %s)",
            (novo_id, titulo, genero_id),
        )
    _replicar_filme(novo_id, titulo, f.genero)
    return {"id": novo_id, "titulo": titulo, "genero": f.genero}


@router.put("/{filme_id}")
def editar(filme_id: str, f: FilmeEntrada):
    titulo = f.titulo.strip()
    with pg() as conn:
        genero_id = _id_genero(conn, f.genero)
        cur = conn.execute(
            "UPDATE filmes SET titulo = %s, genero_id = %s WHERE id = %s",
            (titulo, genero_id, filme_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Filme não encontrado")
    _replicar_filme(filme_id, titulo, f.genero)
    return {"id": filme_id, "titulo": titulo, "genero": f.genero}


@router.delete("/{filme_id}", status_code=204)
def excluir(filme_id: str):
    with pg() as conn:
        cur = conn.execute("DELETE FROM filmes WHERE id = %s", (filme_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Filme não encontrado")
    try:
        with driver.session() as sessao:
            sessao.run("MATCH (f:Filme {id: $id}) DETACH DELETE f", id=filme_id)
    except Exception:
        log.warning("Neo4j indisponível ao excluir filme %s", filme_id)