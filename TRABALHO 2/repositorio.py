"""Persistência do catálogo de filmes em arquivo JSON."""

import json
import os
import threading
from pathlib import Path

from models import Filme, Avaliacao, DISPONIVEL

PASTA_DADOS = Path(__file__).resolve().parent / "dados"

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


class RepositorioFilmes:

    def __init__(self, caminho: Path | None = None):
        self.caminho = Path(caminho) if caminho else PASTA_DADOS / "filmes.json"
        self._trava = threading.Lock()

    def carregar(self) -> list[Filme]:
        if not self.caminho.exists():
            filmes = self._filmes_iniciais()
            self.salvar(filmes)
            return filmes
        try:
            with open(self.caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
            return [Filme.from_dict(d) for d in dados]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            os.replace(self.caminho, self.caminho.with_suffix(".json.bak"))
            filmes = self._filmes_iniciais()
            self.salvar(filmes)
            return filmes

    def salvar(self, filmes: list[Filme]) -> None:
        with self._trava:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            temporario = self.caminho.with_suffix(".json.tmp")
            with open(temporario, "w", encoding="utf-8") as f:
                json.dump([f_.to_dict() for f_ in filmes], f,
                          ensure_ascii=False, indent=2)
            os.replace(temporario, self.caminho)

    @staticmethod
    def _filmes_iniciais() -> list[Filme]:
        return [Filme(t, g, DISPONIVEL) for t, g in FILMES_INICIAIS]


class RepositorioAvaliacoes:

    def __init__(self, caminho: Path | None = None):
        self.caminho = Path(caminho) if caminho else PASTA_DADOS / "avaliacoes.json"
        self._trava = threading.Lock()

    def carregar(self) -> list[Avaliacao]:
        try:
            with open(self.caminho, "r", encoding="utf-8") as f:
                return [Avaliacao.from_dict(d) for d in json.load(f)]
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            return []

    def salvar(self, avaliacoes: list[Avaliacao]) -> None:
        with self._trava:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.caminho.with_suffix(".json.tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump([a.to_dict() for a in avaliacoes], f,
                          ensure_ascii=False, indent=2)
            os.replace(tmp, self.caminho)