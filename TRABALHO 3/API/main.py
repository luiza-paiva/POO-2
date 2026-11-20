from contextlib import asynccontextmanager

from fastapi import FastAPI

import filmes
import alugueis
import usuarios
from db import driver, pg, preparar_neo4j


@asynccontextmanager
async def lifespan(app: FastAPI):
    preparar_neo4j()
    # Administrador padrão, criado só se ainda não existir nenhum
    with pg() as conn:
        existe = conn.execute(
            "SELECT 1 FROM usuarios WHERE tipo = 'Admin' LIMIT 1"
        ).fetchone()
    if not existe:
        usuarios.criar_usuario("admin", "admin", "Admin")
    filmes.semear()
    yield


app = FastAPI(title="Locadora API", lifespan=lifespan)
app.include_router(usuarios.router)
app.include_router(filmes.router)
app.include_router(alugueis.router)


@app.get("/saude")
def saude():
    estado = {}
    try:
        with pg() as conn:
            conn.execute("SELECT 1")
        estado["postgres"] = "ok"
    except Exception as e:
        estado["postgres"] = f"erro: {e}"
    try:
        driver.verify_connectivity()
        estado["neo4j"] = "ok"
    except Exception as e:
        estado["neo4j"] = f"erro: {e}"
    return estado