"""Persistência do catálogo de filmes em arquivo JSON."""

import json
import os
from pathlib import Path

from models import Filme, DISPONIVEL

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
    """Lê e grava a lista de filmes em um arquivo JSON.

    Args:
        caminho: caminho do arquivo. Por padrão, dados/filmes.json.
    """

    def __init__(self, caminho: Path | None = None):
        self.caminho = Path(caminho) if caminho else PASTA_DADOS / "filmes.json"

    def carregar(self) -> list[Filme]:
        """Carrega os filmes do arquivo.

        Se o arquivo não existir, cria o catálogo inicial e o grava.
        Se estiver corrompido, move-o para .bak e recomeça do catálogo inicial.
        """
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
        """Grava os filmes no arquivo de forma atômica.

        Escreve em um arquivo temporário e depois o substitui, evitando
        deixar o JSON pela metade se o programa for interrompido.
        """
        self.caminho.parent.mkdir(parents=True, exist_ok=True)
        temporario = self.caminho.with_suffix(".json.tmp")
        with open(temporario, "w", encoding="utf-8") as f:
            json.dump([f_.to_dict() for f_ in filmes], f,
                      ensure_ascii=False, indent=2)
        os.replace(temporario, self.caminho)

    @staticmethod
    def _filmes_iniciais() -> list[Filme]:
        return [Filme(t, g, DISPONIVEL) for t, g in FILMES_INICIAIS]
