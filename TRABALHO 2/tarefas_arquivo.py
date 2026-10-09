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