# tarefas_arquivo.py
from PySide6.QtCore import QThread, Signal


class GravarDados(QThread):
    concluida = Signal()
    erro = Signal(str)

    def __init__(self, repositorio, filmes, historico=None, registro=None):
        super().__init__()
        self.repositorio = repositorio
        self.filmes = list(filmes)
        self.historico = historico
        self.registro = registro 

    def run(self):
        try:
            self.repositorio.salvar(self.filmes)
            if self.historico and self.registro:
                self.historico.registrar(*self.registro)
            self.concluida.emit()
        except Exception as e:
            self.erro.emit(str(e))
            
class CarregarHistorico(QThread):
    carregado = Signal(list)
    erro = Signal(str)

    def __init__(self, historico):
        super().__init__()
        self.historico = historico

    def run(self):
        try:
            self.carregado.emit(self.historico.carregar())
        except Exception as e:
            self.erro.emit(str(e))

    class ExportarHistorico(QThread):
        exportado = Signal(str)
        erro = Signal(str)

        def __init__(self, registros,caminho):
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