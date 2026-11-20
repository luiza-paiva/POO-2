import logging
import os

import psycopg
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

log = logging.getLogger("locadora")

PG_DSN = os.environ["PG_DSN"]
NEO4J_URI = os.environ["NEO4J_URI"]
NEO4J_USER = os.environ["NEO4J_USER"]
NEO4J_PASSWORD = os.environ["NEO4J_PASSWORD"]

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def pg():
    return psycopg.connect(PG_DSN)


def preparar_neo4j() -> None:
    comandos = [
        "CREATE CONSTRAINT usuario_login IF NOT EXISTS "
        "FOR (u:Usuario) REQUIRE u.login IS UNIQUE",
        "CREATE CONSTRAINT filme_id IF NOT EXISTS "
        "FOR (f:Filme) REQUIRE f.id IS UNIQUE",
        "CREATE CONSTRAINT genero_nome IF NOT EXISTS "
        "FOR (g:Genero) REQUIRE g.nome IS UNIQUE",
    ]
    try:
        with driver.session() as sessao:
            for comando in comandos:
                sessao.run(comando)
    except Exception:
        log.warning("Neo4j indisponível ao criar constraints")