import logging

import bcrypt
from fastapi import APIRouter, HTTPException
from psycopg.errors import UniqueViolation
from pydantic import BaseModel, Field

from db import driver, pg

log = logging.getLogger("locadora")

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


class Credenciais(BaseModel):
    login: str = Field(min_length=3, max_length=50)
    senha: str = Field(min_length=4, max_length=72)


def criar_usuario(login: str, senha: str, tipo: str) -> None:
    """Grava no Postgres (fonte da verdade) e depois replica no Neo4j."""
    senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
    with pg() as conn:
        conn.execute(
            "INSERT INTO usuarios (login, senha_hash, tipo) VALUES (%s, %s, %s)",
            (login, senha_hash, tipo),
        )
    try:
        with driver.session() as sessao:
            sessao.run("MERGE (:Usuario {login: $login})", login=login)
    except Exception:
        log.warning("Neo4j indisponível ao replicar usuário %s", login)


@router.post("/cadastro", status_code=201)
def cadastro(c: Credenciais):
    try:
        criar_usuario(c.login, c.senha, "Usuario")
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Login já existe")
    return {"login": c.login, "tipo": "Usuario"}


@router.post("/login")
def login(c: Credenciais):
    with pg() as conn:
        linha = conn.execute(
            "SELECT senha_hash, tipo FROM usuarios WHERE login = %s", (c.login,)
        ).fetchone()
    if not linha or not bcrypt.checkpw(c.senha.encode(), linha[0].encode()):
        raise HTTPException(status_code=401, detail="Login ou senha inválidos")
    return {"login": c.login, "tipo": linha[1]}