import json
import threading
from pathlib import Path
from repositorio import PASTA_DADOS

class registroUsuarios:
    def __init__(self, caminho: Path | None = None):
        self.caminho = Path(caminho) if caminho else PASTA_DADOS / "usuarios.json"
        self._trava = threading.RLock()

    def _carregar(self):
        if not self.caminho.exists():
            usuarios = [{
                "login": "admin",
                "senha": "admin",
                "tipo": "Admin"
            }]
            self._salvar(usuarios)
            return usuarios

        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except(json.JSONDecodeError, OSError):
            return []

    def _salvar(self, usuarios):
        with self._trava:
            self.caminho.parent.mkdir(parents=True, exist_ok=True)
            with open(self.caminho, "w", encoding="utf-8") as arquivo:
                json.dump(usuarios, arquivo, ensure_ascii=False, indent=2)

    def cadastrar(self,login:str, senha:str, tipo:str = "Usuário"):
        with self._trava:
            usuarios = self._carregar()
            for u in usuarios:
                if(u["login"] == login):
                    return False
            usuarios.append({"login": login, "senha": senha, "tipo": tipo})
            self._salvar(usuarios)
            return True

    def validar(self, login:str, senha:str):
        with self._trava:
            usuarios = self._carregar()
        for u in usuarios:
            if(u["login"] == login and u["senha"] == senha):
                return u["tipo"]
        return  None