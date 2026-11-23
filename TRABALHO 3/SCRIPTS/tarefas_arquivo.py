from PySide6.QtCore import QThread, Signal

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
