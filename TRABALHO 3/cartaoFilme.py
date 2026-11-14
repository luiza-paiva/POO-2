import sys, os
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QApplication, QWidget, QHBoxLayout, QGraphicsPixmapItem, QStyle
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal

LARGURA = 160
ALTURA_IMAGEM = 230
PASTA_POSTERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posters")

CORES_GENERO = {
    "romance": "#b83b5e",
    "ação": "#c0392b",
    "drama": "#34495e",
    "terror": "#4a235a",
    "ficção científica": "#1f6f8b",
}

class CartaoFilme(QFrame):
    clicado = Signal(int)

    def __init__(self, filme):
        super().__init__()
        self.filmeId = filme.id
        self.setObjectName("cartao")
        self.setFixedWidth(LARGURA)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 6)
        layout.setSpacing(4)

        self.imagem = QLabel()
        self.imagem.setFixedSize(LARGURA, ALTURA_IMAGEM)
        self.imagem.setAlignment(Qt.AlignCenter)
        self._carregar_poster(filme)
        layout.addWidget(self.imagem)

        self.titulo = QLabel(filme.titulo)
        self.titulo.setWordWrap(True)
        self.titulo.setContentsMargins(6, 0, 6, 0)
        layout.addWidget(self.titulo)
        self.titulo.setMinimumHeight(44)
        self.titulo.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.titulo.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.titulo)
        self.titulo.setStyleSheet("font-size: 14px; font-weight: bold; background: transparent;")

        self.status = QLabel()
        self.status.setContentsMargins(6, 0, 6, 0)
        layout.addWidget(self.status)
        self.atualizar_status(filme.disponivel)
        self.titulo.setStyleSheet("font-size: 14px; font-weight: bold; background: transparent;")

    def _carregar_poster(self, filme):
        pixmap = QPixmap(os.path.join(PASTA_POSTERS, f"{filme.id}.jpg"))
        if pixmap.isNull():
            cor = CORES_GENERO.get(filme.genero, "#444444")
            self.imagem.setStyleSheet(f"background-color: {cor}; color: white; font-weight: bold;")
            self.imagem.setWordWrap(True)
            self.imagem.setText(filme.titulo)
        else:
            self.imagem.setPixmap(pixmap.scaled(
                LARGURA, ALTURA_IMAGEM,
                Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    def atualizar_status(self, disponivel):
        if disponivel:
            self.status.setText("Disponível")
            self.status.setStyleSheet("color: #2ecc71; font-size: 11px; background: transparent;")
        else:
            self.status.setText("Alugado")
            self.status.setStyleSheet("color: #e74c3c; font-size: 11px; background: transparent;")

    def set_selecionado(self, selecionado):
        self.setProperty("selecionado", selecionado)
        self.style().unpolish(self)
        self.style().polish(self)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicado.emit(self.filmeId)
        super().mousePressEvent(event)



if __name__ == "__main__":
    class FilmeFalso:
        def __init__(self, id, titulo, genero, disponivel):
            self.id, self.titulo, self.genero, self.disponivel = id, titulo, genero, disponivel

    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget { background-color: #141414; color: white; }
        QFrame#cartao { background-color: #1f1f1f; border-radius: 8px; border: 2px solid transparent; }
        QFrame#cartao:hover { background-color: #2a2a2a; }
        QFrame#cartao[selecionado="true"] { border: 2px solid #e50914; }
    """)

    janela = QWidget()
    linha = QHBoxLayout(janela)
    cartoes = []
    filmes = [
        FilmeFalso(1, "O Poderoso Chefão", "drama", True),
        FilmeFalso(2, "Pânico", "terror", False),
        FilmeFalso(3, "Duna", "ficção científica", True),
    ]

    def ao_clicar(id_filme):
        print("clicou no filme", id_filme)
        for c in cartoes:
            c.set_selecionado(c.filmeId == id_filme)

    for f in filmes:
        c = CartaoFilme(f)
        c.clicado.connect(ao_clicar)
        cartoes.append(c)
        linha.addWidget(c)

    janela.show()
    sys.exit(app.exec())