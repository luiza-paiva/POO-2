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

SINOPSES = {
    "O Poderoso Chefão": "A família Corleone é a mais poderosa da máfia de Nova York. Quando o patriarca é ferido num atentado, o filho caçula, que sempre quis ficar longe dos negócios da família, é puxado para o centro da disputa pelo poder.",
    "Pânico": "Numa cidade pequena e tranquila, um assassino mascarado persegue adolescentes por telefone antes de atacar. Sidney, ainda abalada pela morte da mãe, percebe que conhecer as regras dos filmes de terror pode decidir quem sobrevive.",
    "Duna": "No planeta deserto Arrakis, única fonte da especiaria mais valiosa do universo, o jovem Paul Atreides vê a família ser lançada numa disputa mortal e precisa descobrir o destino que o espera entre os povos do deserto.",
    "Titanic": "Em 1912, Rose, noiva de um homem rico que ela não ama, conhece Jack, um artista sem dinheiro, a bordo do navio mais luxuoso do mundo. O romance dos dois começa poucos dias antes do desastre.",
    "Interestelar": "Com a Terra perdendo a capacidade de produzir alimentos, um ex-piloto parte por um buraco de minhoca em busca de um novo lar para a humanidade, sabendo que cada hora no espaço custa anos longe da família.",
    "John Wick": "Um ex-assassino aposentado, que tentava recomeçar depois de perder a esposa, vê o passado voltar quando bandidos invadem sua casa. Ele retorna ao submundo do crime para acertar as contas.",
    "Invocação do Mal": "Um casal de investigadores do sobrenatural ajuda uma família que se mudou para uma casa isolada no campo e passou a ser atormentada por uma presença cada vez mais violenta.",
    "Orgulho e Preconceito": "Na Inglaterra do século XIX, Elizabeth Bennet não quer se casar por conveniência. Seu caminho cruza com o do reservado e orgulhoso Sr. Darcy, e os dois precisam rever as primeiras impressões que tiveram um do outro.",
    "Clube da Luta": "Um funcionário insone, cansado da própria rotina, conhece um vendedor de sabão carismático. Juntos criam um clube secreto de lutas que cresce muito além do que eles imaginavam.",
    "Mad Max: Estrada da Fúria": "Num deserto pós-apocalíptico, Furiosa foge com um grupo de mulheres do tirano que as mantinha presas. Max, um sobrevivente solitário, acaba envolvido nessa perseguição por uma estrada que parece não ter fim.",
    "Corra!": "Chris vai conhecer a família da namorada num fim de semana no interior. A recepção calorosa vai dando lugar a pequenos detalhes estranhos, e ele percebe que há algo muito errado naquela casa.",
    "Blade Runner 2049": "Num futuro sombrio, um novo caçador de androides descobre um segredo capaz de abalar a fronteira entre humanos e replicantes. A busca por respostas o leva até Rick Deckard, desaparecido há décadas.",
    "Diário de uma Paixão": "Num lar de idosos, um senhor lê para uma mulher a história de Noah e Allie, jovens de classes sociais diferentes que se apaixonam num verão e são separados pela família e pela guerra.",
    "Cidade de Deus": "Nas décadas de 1960 e 1970, Buscapé cresce na comunidade que dá nome ao filme vendo amigos se tornarem criminosos. Sonhando em ser fotógrafo, ele conta a ascensão de Zé Pequeno ao comando do tráfico.",
    "Um Sonho de Liberdade": "Condenado à prisão perpétua por um crime que diz não ter cometido, o banqueiro Andy Dufresne faz amizade com Red e passa décadas na penitenciária de Shawshank, mantendo viva a esperança de ser livre um dia.",
}


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
            filmes = [Filme.from_dict(d) for d in dados]
            alterou = False
            for f in filmes:
                if not f.sinopse and f.titulo in SINOPSES:
                    f.sinopse = SINOPSES[f.titulo]
                    alterou = True
            if alterou:
                self.salvar(filmes)
            return filmes
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
        return [Filme(t, g, DISPONIVEL, sinopse=SINOPSES.get(t, "")) for t, g in FILMES_INICIAIS]


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