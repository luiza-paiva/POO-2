import os
from urllib.parse import quote

import requests

# Endereço do servidor na rede Tailscale. Para testar localmente, defina
# a variável de ambiente LOCADORA_API (ex.: http://localhost:8000).
SERVIDOR_PADRAO = "http://100.122.141.42:8000"
URL_BASE = os.environ.get("LOCADORA_API", SERVIDOR_PADRAO).rstrip("/")
TEMPO_LIMITE = 5

TIPOS_IMAGEM = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

class ErroApi(Exception):
    pass

def baixar_poster(filme_id):
    try:
        resposta = requests.get(f"{URL_BASE}/posters/{filme_id}", timeout=TEMPO_LIMITE)
    except requests.exceptions.RequestException:
        raise ErroApi("API fora do ar")
    if resposta.status_code == 404:
        return None
    if resposta.status_code != 200:
        raise ErroApi(_detalhe(resposta))
    tipo = resposta.headers.get("Content-Type", "").split(";")[0]
    return resposta.content, TIPOS_IMAGEM.get(tipo, ".jpg")


def _detalhe(resposta):
    try:
        detalhe = resposta.json().get("detail", resposta.text)
    except ValueError:
        return resposta.text
    if isinstance(detalhe, list):
        return "; ".join(d.get("msg", "") for d in detalhe)
    return str(detalhe)


def login(login, senha):
    try:
        resposta = requests.post(
            f"{URL_BASE}/usuarios/login",
            json={"login": login, "senha": senha},
            timeout=TEMPO_LIMITE,
        )
    except requests.exceptions.RequestException:
        raise ErroApi("API fora do ar")

    if resposta.status_code == 200:
        return resposta.json()["tipo"]
    if resposta.status_code == 401:
        return None
    raise ErroApi(_detalhe(resposta))

def cadastrar(login, senha):
    try:
        resposta = requests.post(
            f"{URL_BASE}/usuarios/cadastro",
            json={"login": login, "senha": senha},
            timeout=TEMPO_LIMITE,
        )
    except requests.exceptions.RequestException:
        raise ErroApi("API fora do ar")

    if resposta.status_code == 201:
        return True
    if resposta.status_code == 409:
        return False
    raise ErroApi(_detalhe(resposta))

def listar_filmes(login=None):
    params = {"login": login} if login else None
    try:
        resposta = requests.get(f"{URL_BASE}/filmes", params=params, timeout=TEMPO_LIMITE)
    except requests.exceptions.RequestException:
        raise ErroApi("API fora do ar")

    if resposta.status_code == 200:
        return resposta.json()
    raise ErroApi(_detalhe(resposta))

def listar_recomendados(login):
    try:
        resposta = requests.get(
            f"{URL_BASE}/filmes/recomendados/{quote(login, safe='')}",
            timeout=TEMPO_LIMITE,
        )
    except requests.exceptions.RequestException:
        raise ErroApi("API fora do ar")

    if resposta.status_code == 200:
        return resposta.json()
    raise ErroApi(_detalhe(resposta))

def _enviar(caminho, login, filme_id):
    try:
        resposta = requests.post(
            f"{URL_BASE}{caminho}",
            json={"login": login, "filme_id": filme_id},
            timeout=TEMPO_LIMITE,
        )
    except requests.exceptions.RequestException:
        raise ErroApi("API fora do ar")
    if resposta.status_code not in (200, 201):
        raise ErroApi(_detalhe(resposta))


def alugar(login, filme_id):
    _enviar("/alugueis", login, filme_id)


def devolver(login, filme_id):
    _enviar("/alugueis/devolucao", login, filme_id)

def historico(usuario=None):
    params = {"usuario": usuario} if usuario else None
    try:
        resposta = requests.get(
            f"{URL_BASE}/alugueis/historico", params=params, timeout=TEMPO_LIMITE
        )
    except requests.exceptions.RequestException:
        raise ErroApi("API fora do ar")
    if resposta.status_code == 200:
        return resposta.json()
    raise ErroApi(_detalhe(resposta))

def _requisitar(metodo, caminho, corpo=None):
    try:
        resposta = requests.request(
            metodo, f"{URL_BASE}{caminho}", json=corpo, timeout=TEMPO_LIMITE
        )
    except requests.exceptions.RequestException:
        raise ErroApi("API fora do ar")
    if resposta.status_code not in (200, 201, 204):
        raise ErroApi(_detalhe(resposta))

def cadastrar_filme(titulo, genero, sinopse="", copias=1):
    _requisitar("POST", "/filmes", {"titulo": titulo, "genero": genero, "sinopse": sinopse, "copias": copias})

def editar_filme(filme_id, titulo, genero, sinopse="", copias=1):
    _requisitar("PUT", f"/filmes/{filme_id}", {"titulo": titulo, "genero": genero, "sinopse": sinopse, "copias": copias})

def excluir_filme(filme_id):
    _requisitar("DELETE", f"/filmes/{filme_id}")

def avaliar(login, filme_id, nota, comentario=""):
    _requisitar(
        "POST",
        "/avaliacoes",
        {"login": login, "filme_id": filme_id, "nota": nota, "comentario": comentario},
    )

def listar_avaliacoes(filme_id):
    try:
        resposta = requests.get(
            f"{URL_BASE}/avaliacoes/{filme_id}", timeout=TEMPO_LIMITE
        )
    except requests.exceptions.RequestException:
        raise ErroApi("API fora do ar")
    if resposta.status_code == 200:
        return resposta.json()
    raise ErroApi(_detalhe(resposta))

if __name__ == "__main__":
    filmes = listar_filmes()
    print(len(filmes), "filmes")
    print(filmes[0])