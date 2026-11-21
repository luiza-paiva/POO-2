"""Modelos de dados da locadora."""

import uuid
from dataclasses import dataclass, field, asdict

GENEROS = ["romance", "ação", "drama", "terror", "ficção científica"]
DISPONIVEL = "Disponível"
ALUGADO = "Alugado"


@dataclass
class Filme:

    titulo: str
    genero: str
    status: str = DISPONIVEL
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    alugado_por: str = ""      # login de quem alugou
    data_aluguel: str = ""     # "dd/mm/aaaa HH:MM:SS"
    sinopse: str = ""

    @property
    def disponivel(self) -> bool:
        return self.status == DISPONIVEL

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, dados: dict) -> "Filme":
        return cls(
            titulo=str(dados["titulo"]),
            genero=str(dados["genero"]),
            status=str(dados.get("status", DISPONIVEL)),
            id=str(dados.get("id") or uuid.uuid4().hex),
            alugado_por=str(dados.get("alugado_por", "")),
            data_aluguel=str(dados.get("data_aluguel", "")),
            sinopse=str(dados.get("sinopse", "")),
        )

    def __str__(self) -> str:
        return f"{self.titulo} ({self.genero}) - {self.status}"


@dataclass
class Avaliacao:
    filme_id: str
    usuario: str
    nota: int         
    comentario: str = ""
    data_hora: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Avaliacao":
        return cls(str(d["filme_id"]), str(d["usuario"]), int(d["nota"]),
                   str(d.get("comentario", "")), str(d.get("data_hora", "")))