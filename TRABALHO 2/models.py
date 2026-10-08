"""Modelos de dados da locadora."""

import uuid
from dataclasses import dataclass, field, asdict

GENEROS = ["romance", "ação", "drama", "terror", "ficção científica"]
DISPONIVEL = "Disponível"
ALUGADO = "Alugado"


@dataclass
class Filme:
    """Representa um filme do catálogo.

    Atributos:
        titulo: título do filme.
        genero: um dos valores de GENEROS.
        status: DISPONIVEL ou ALUGADO.
        id: identificador único (UUID em hexadecimal), usado para localizar
            o filme mesmo quando a lista exibida está filtrada.
    """

    titulo: str
    genero: str
    status: str = DISPONIVEL
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    @property
    def disponivel(self) -> bool:
        return self.status == DISPONIVEL

    def to_dict(self) -> dict:
        """Converte o filme em dicionário (serializável em JSON)."""
        return asdict(self)

    @classmethod
    def from_dict(cls, dados: dict) -> "Filme":
        """Cria um Filme a partir de um dicionário lido do JSON."""
        return cls(
            titulo=str(dados["titulo"]),
            genero=str(dados["genero"]),
            status=str(dados.get("status", DISPONIVEL)),
            id=str(dados.get("id") or uuid.uuid4().hex),
        )

    def __str__(self) -> str:
        return f"{self.titulo} ({self.genero}) - {self.status}"
