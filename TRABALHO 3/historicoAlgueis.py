import csv
import threading
from datetime import datetime
from pathlib import Path

from repositorio import PASTA_DADOS

CAMPOS = ["data_hora", "usuario", "filme", "acao"]

class historico():
    def __init__(self, caminho: Path | None = None):
        self.caminho = Path(caminho) if caminho else PASTA_DADOS / "alugueis.csv"
        self._trava = threading.Lock()

    def registrar(self,usuario, filme, acao):
        #acao é devolução ou aluguel
        with self._trava:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            arquivo_novo = not self.caminho.exists()
            with open(self.caminho, "a", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS, delimiter=";")
                if arquivo_novo:
                    escritor.writeheader()
                escritor.writerow({
                    'data_hora': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    'usuario': usuario,
                    'filme': filme,
                    'acao': acao
                })
    def carregar(self):
        with self._trava:
            if not self.caminho.exists():
                return []
            with open(self.caminho, "r", newline="", encoding="utf-8-sig") as arquivo:
                registros = list(csv.DictReader(arquivo, delimiter=";"))
        registros.reverse()
        return registros