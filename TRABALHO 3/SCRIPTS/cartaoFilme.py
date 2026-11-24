import sys, os, re, unicodedata
from PySide6.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout, QApplication, QWidget,
    QScrollArea, QPushButton
)
from PySide6.QtGui import (
    QPixmap, QPainter, QColor, QLinearGradient, QFont, QPainterPath, QTextOption
)
from PySide6.QtCore import Qt, Signal, QRectF, QPropertyAnimation, QEasingCurve, QTimer


LARGURA = 196
LARGURA_POSTER = 170
ALTURA_POSTER = 250
ALTURA_CARTAO = 352
ESPACO_CARTOES = 14
PASTA_POSTERS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posters")
PASTA_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dados", "cache_posters")

CORES_GENERO = {
    "romance": "#b83b5e",
    "ação": "#c0392b",
    "drama": "#34495e",
    "terror": "#4a235a",
    "ficção científica": "#1f6f8b",
}
COR_ESTRELA = "#f5b301"


EXTENSOES = (".jpg", ".jpeg", ".png", ".webp")


def nome_arquivo_poster(titulo):
    texto = unicodedata.normalize("NFKD", titulo).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", texto.lower()).strip("_")


def caminho_poster(filme):
    for pasta in (PASTA_POSTERS, PASTA_CACHE):
        for nome in (nome_arquivo_poster(filme.titulo), filme.id):
            for ext in EXTENSOES:
                caminho = os.path.join(pasta, nome + ext)
                if os.path.exists(caminho):
                    return caminho
    return ""


def formatar_nota(media, qtd):
    if qtd == 0:
        return "Sem avaliações"
    nota = f"{media:.1f}".replace(".", ",")
    return f"<span style='color:{COR_ESTRELA}'>★</span> {nota} ({qtd})"


def gerar_poster(filme, largura, altura, raio=10):
    dpr = 2
    base = QPixmap(largura * dpr, altura * dpr)
    base.setDevicePixelRatio(dpr)
    base.fill(Qt.transparent)

    p = QPainter(base)
    p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform
                     | QPainter.TextAntialiasing)
    recorte = QPainterPath()
    recorte.addRoundedRect(QRectF(0, 0, largura, altura), raio, raio)
    p.setClipPath(recorte)

    arquivo = QPixmap(caminho_poster(filme))
    if not arquivo.isNull():
        esc = arquivo.scaled(largura * dpr, altura * dpr,
                             Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        w, h = esc.width() / dpr, esc.height() / dpr
        p.drawPixmap(QRectF((largura - w) / 2, (altura - h) / 2, w, h),
                     esc, QRectF(esc.rect()))
    else:
        cor = QColor(CORES_GENERO.get(filme.genero, "#444444"))
        grad = QLinearGradient(0, 0, 0, altura)
        grad.setColorAt(0, cor.lighter(130))
        grad.setColorAt(1, cor.darker(180))
        p.fillRect(0, 0, largura, altura, grad)

        fonte = QFont()
        fonte.setBold(True)
        fonte.setPixelSize(int(altura * 0.5))
        p.setFont(fonte)
        p.setPen(QColor(255, 255, 255, 80))
        p.drawText(QRectF(0, 0, largura, altura),
                   filme.titulo[:1].upper(), QTextOption(Qt.AlignCenter))
    p.end()
    return base


class CartaoFilme(QFrame):
    clicado = Signal(str)

    def __init__(self, filme, media=0.0, qtd=0):
        super().__init__()
        self.filme_id = filme.id
        self.setObjectName("cartao")
        self.setFixedSize(LARGURA, ALTURA_CARTAO)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"{filme.titulo}\nClique para ver os detalhes")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(11, 11, 11, 10)
        layout.setSpacing(7)

        self.imagem = QLabel()
        self.imagem.setFixedSize(LARGURA_POSTER, ALTURA_POSTER)
        self.imagem.setPixmap(gerar_poster(filme, LARGURA_POSTER, ALTURA_POSTER))
        layout.addWidget(self.imagem)

        self.selo = QLabel(self.imagem)
        self.selo.move(8, 8)
        self.atualizar_status(filme)

        self.titulo = QLabel(filme.titulo)
        self.titulo.setObjectName("cartaoTitulo")
        self.titulo.setWordWrap(True)
        self.titulo.setFixedHeight(38)
        self.titulo.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.titulo)

        self.nota = QLabel(formatar_nota(media, qtd))
        self.nota.setObjectName("cartaoNota")
        layout.addWidget(self.nota)
        layout.addStretch()

    def atualizar_status(self, filme):
        disponivel = filme.disponivel
        cor = "rgba(30, 140, 80, 235)" if disponivel else "rgba(185, 55, 45, 235)"
        if disponivel:
            self.selo.setText(f"Disponível {filme.copias_disponiveis}/{filme.copias}")
        else:
            self.selo.setText("Indisponível")
        self.selo.setStyleSheet(
            f"background: {cor}; color: white; font-size: 11px; font-weight: bold;"
            "border-radius: 9px; padding: 3px 9px;")
        self.selo.adjustSize()

    def set_selecionado(self, selecionado):
        self.setProperty("selecionado", selecionado)
        self.style().unpolish(self)
        self.style().polish(self)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.position().toPoint()):
            QTimer.singleShot(0, lambda fid=self.filme_id: self.clicado.emit(fid))
        super().mouseReleaseEvent(event)


class _RolagemHorizontal(QScrollArea):
    def wheelEvent(self, event):
        d = event.angleDelta()
        if abs(d.x()) > abs(d.y()):
            super().wheelEvent(event)
        else:
            event.ignore()


class FileiraGenero(QWidget):
    clicado = Signal(str)

    def __init__(self, genero, filmes, notas=None):
        super().__init__()
        notas = notas or {}
        self.cartoes = []
        self._anim = None

        layoutExterno = QVBoxLayout(self)
        layoutExterno.setContentsMargins(0, 0, 0, 0)
        layoutExterno.setSpacing(6)

        titulo = QLabel(genero.capitalize())
        titulo.setObjectName("tituloFileira")
        self.setaEsq = QPushButton("‹")
        self.setaDir = QPushButton("›")
        for seta, direcao in ((self.setaEsq, -1), (self.setaDir, 1)):
            seta.setObjectName("setaFileira")
            seta.setCursor(Qt.PointingHandCursor)
            seta.clicked.connect(lambda _, d=direcao: self._rolar(d))

        cabecalho = QHBoxLayout()
        cabecalho.addWidget(titulo)
        cabecalho.addStretch()
        cabecalho.addWidget(self.setaEsq)
        cabecalho.addWidget(self.setaDir)
        layoutExterno.addLayout(cabecalho)

        self.scroll = _RolagemHorizontal()
        self.conteudo = QWidget()
        self.conteudo.setAutoFillBackground(False)
        layoutCartoes = QHBoxLayout(self.conteudo)
        layoutCartoes.setContentsMargins(0, 0, 0, 0)
        layoutCartoes.setSpacing(ESPACO_CARTOES)

        for filme in filmes:
            media, qtd = notas.get(filme.id, (0.0, 0))
            cartao = CartaoFilme(filme, media, qtd)
            cartao.clicado.connect(self.clicado)
            layoutCartoes.addWidget(cartao)
            self.cartoes.append(cartao)
        layoutCartoes.addStretch()

        self.scroll.setWidget(self.conteudo)
        self.scroll.setWidgetResizable(True)
        self.scroll.viewport().setAutoFillBackground(False)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll.setFixedHeight(ALTURA_CARTAO + 16)
        layoutExterno.addWidget(self.scroll)

        barra = self.scroll.horizontalScrollBar()
        barra.rangeChanged.connect(lambda _mn, mx: self._mostrar_setas(mx > 0))
        self._mostrar_setas(False)

    def _mostrar_setas(self, visivel):
        self.setaEsq.setVisible(visivel)
        self.setaDir.setVisible(visivel)

    def _rolar(self, direcao):
        barra = self.scroll.horizontalScrollBar()
        passo = (LARGURA + ESPACO_CARTOES) * 2
        destino = max(barra.minimum(), min(barra.maximum(), barra.value() + direcao * passo))
        self._anim = QPropertyAnimation(barra, b"value", self)
        self._anim.setDuration(260)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.setEndValue(destino)
        self._anim.start()


if __name__ == "__main__":
    import tema

    class FilmeFalso:
        def __init__(self, id, titulo, genero, disponivel):
            self.id, self.titulo, self.genero, self.disponivel = id, titulo, genero, disponivel

    app = QApplication(sys.argv)
    tema.aplicar_tema(tema.carregar_preferencia())

    filmes = [FilmeFalso(str(i), f"Filme {i}", "drama", i % 2 == 0) for i in range(1, 11)]
    notas = {"1": (4.5, 3), "2": (3.0, 1)}

    janela = QWidget()
    layout = QVBoxLayout(janela)
    fileira = FileiraGenero("drama", filmes, notas)

    def ao_clicar(id_filme):
        print("clicou no filme", id_filme)
        for c in fileira.cartoes:
            c.set_selecionado(c.filme_id == id_filme)

    fileira.clicado.connect(ao_clicar)
    layout.addWidget(fileira)
    layout.addStretch()
    janela.resize(800, 460)
    janela.show()
    sys.exit(app.exec())