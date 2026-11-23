import os
from PySide6.QtCore import QThread, Signal

import clienteApi
from cartaoFilme import PASTA_CACHE, caminho_poster

class BaixarPosters(QThread):
    baixado = Signal()

    def __init__(self, filmes):
        super().__init__()
        self.filmes = filmes

    def run(self):
        novo = False
        os.makedirs(PASTA_CACHE, exist_ok=True)
        for filme in self.filmes:
            try:
                resultado = clienteApi.baixar_poster(filme.id)
            except clienteApi.ErroApi:
                break
            if resultado is None:
                continue
            dados, ext = resultado
            with open(os.path.join(PASTA_CACHE, filme.id + ext), "wb") as f:
                f.write(dados)
            novo = True
        if novo:
            self.baixado.emit()


class ExportarHistorico(QThread):
    exportado = Signal(str)
    erro = Signal(str)

    def __init__(self, registros, caminho):
        super().__init__()
        self.registros = registros
        self.caminho = caminho

    def run(self):
        try:
            with open(self.caminho, "w", encoding="utf-8") as f:
                for r in self.registros:
                    f.write(f"{r['data_hora']} - {r['usuario']} - {r['filme']} - {r['acao']}\n")
            self.exportado.emit(self.caminho)
        except Exception as e:
            self.erro.emit(str(e))
