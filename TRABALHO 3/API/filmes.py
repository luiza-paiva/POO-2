import logging
import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db import driver, pg

log = logging.getLogger("locadora")

router = APIRouter(prefix="/filmes", tags=["filmes"])

GENEROS = ["romance", "ação", "drama", "terror", "ficção científica"]

FILMES_INICIAIS = [
    ("O Poderoso Chefão", "drama", "A saga da família mafiosa Corleone, que vê o poder passar das mãos do patriarca para o filho mais novo, que nunca quis esse caminho."),
    ("Pânico", "terror", "Uma cidadezinha é aterrorizada por um assassino mascarado que liga para as vítimas antes de atacar, e uma adolescente se torna o alvo."),
    ("Duna", "ficção científica", "Num futuro distante, o jovem Paul Atreides viaja para o planeta deserto Arrakis, fonte da substância mais valiosa do universo, e se vê no centro de uma guerra."),
    ("Titanic", "romance", "Um artista pobre e uma jovem da alta sociedade se apaixonam a bordo do navio mais luxuoso do mundo, durante sua primeira e trágica viagem."),
    ("Interestelar", "ficção científica", "Com a Terra à beira do colapso, um ex-piloto lidera uma missão por um buraco de minhoca em busca de um novo lar para a humanidade."),
    ("John Wick", "ação", "Um ex-assassino aposentado volta ao submundo do crime para se vingar de quem matou o cachorro que ganhou de sua esposa falecida."),
    ("Invocação do Mal", "terror", "Os investigadores paranormais Ed e Lorraine Warren ajudam uma família atormentada por uma presença sombria em sua casa de fazenda."),
    ("Orgulho e Preconceito", "romance", "Na Inglaterra do século XIX, Elizabeth Bennet precisa superar o orgulho do rico Sr. Darcy e os próprios preconceitos para descobrir o amor."),
    ("Clube da Luta", "drama", "Um funcionário entediado e insone cria, com um vendedor de sabonetes carismático, um clube secreto de lutas que foge do controle."),
    ("Mad Max: Estrada da Fúria", "ação", "Num deserto pós-apocalíptico, Max se une à imperatriz Furiosa numa fuga alucinante contra o tirano Immortan Joe e seu exército."),
    ("Corra!", "terror", "Um fotógrafo negro vai conhecer a família da namorada no interior e percebe que a hospitalidade esconde algo muito perturbador."),
    ("Blade Runner 2049", "ficção científica", "Um novo caçador de androides descobre um segredo capaz de abalar a ordem da sociedade e parte em busca de um antigo blade runner desaparecido."),
    ("Diário de uma Paixão", "romance", "Um idoso lê para uma mulher a história de um amor de verão entre um rapaz humilde e uma moça rica, separados pela família e pela guerra."),
    ("Cidade de Deus", "drama", "Dois garotos crescem na favela carioca nas décadas de 60 e 70: um sonha em ser fotógrafo, o outro se torna o chefe do tráfico."),
    ("Um Sonho de Liberdade", "drama", "Condenado injustamente por duplo homicídio, um banqueiro faz amizade na prisão e nunca abandona a esperança de ser livre."),
]

class FilmeEntrada(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    genero: str
    sinopse: str = ""


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
        "sinopse": l[7],
    }


def semear() -> None:
    novos = []
    with pg() as conn:
        for g in GENEROS:
            conn.execute(
                "INSERT INTO generos (nome) VALUES (%s) ON CONFLICT (nome) DO NOTHING",
                (g,),
            )
        vazio = conn.execute("SELECT NOT EXISTS (SELECT 1 FROM filmes)").fetchone()[0]
        if vazio:
            for titulo, genero, sinopse in FILMES_INICIAIS:
                fid = uuid.uuid4().hex
                conn.execute(
                    "INSERT INTO filmes (id, titulo, genero_id, sinopse) "
                    "SELECT %s, %s, id, %s FROM generos WHERE nome = %s",
                    (fid, titulo, sinopse, genero),
                )
                novos.append((fid, titulo, genero))
        for titulo, _, sinopse in FILMES_INICIAIS:
            conn.execute(
                "UPDATE filmes SET sinopse = %s WHERE titulo = %s AND sinopse = ''",
                (sinopse, titulo),
            )
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
                COALESCE(av.media, 0), COALESCE(av.qtd, 0), f.sinopse
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
            "INSERT INTO filmes (id, titulo, genero_id, sinopse) VALUES (%s, %s, %s, %s)",
            (novo_id, titulo, genero_id, f.sinopse.strip()),
        )
    _replicar_filme(novo_id, titulo, f.genero)
    return {"id": novo_id, "titulo": titulo, "genero": f.genero}


@router.put("/{filme_id}")
def editar(filme_id: str, f: FilmeEntrada):
    titulo = f.titulo.strip()
    with pg() as conn:
        genero_id = _id_genero(conn, f.genero)
        cur = conn.execute(
            "UPDATE filmes SET titulo = %s, genero_id = %s, sinopse = %s WHERE id = %s",
            (titulo, genero_id, f.sinopse.strip(), filme_id),
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