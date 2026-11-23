from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QListWidget,
    QDialog, QFormLayout, QComboBox, QPlainTextEdit, QCheckBox, QHBoxLayout,
    QSpinBox
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal
import tema


class JanelaAlugar(QDialog):
    def __init__(self, titulo_filme="", genero_filme=""):
        super().__init__()
        self.setWindowTitle("Alugar Filme")
        self.resize(300, 150)

        self.campoFilme = QLineEdit(titulo_filme)
        self.campoFilme.setEnabled(False)

        self.campoGenero = QLineEdit(genero_filme)
        self.campoGenero.setEnabled(False)

        self.botaoConfirmar = QPushButton("Confirmar Aluguel")
        self.botaoConfirmar.clicked.connect(self.accept)

        layout = QFormLayout()
        layout.addRow("Filme:", self.campoFilme)
        layout.addRow("Gênero:", self.campoGenero)
        layout.addRow(self.botaoConfirmar)
        self.setLayout(layout)


class JanelaCadastro(QDialog):
    def __init__(self, titulo="", genero="", sinopse="", copias=1):
        super().__init__()
        self.setWindowTitle("Cadastrar/Editar Filme")
        self.resize(420, 330)

        self.campoTitulo = QLineEdit(titulo)
        self.campoGenero = QComboBox()
        self.campoGenero.addItems(["romance", "ação", "drama", "terror", "ficção científica"])

        self.campoCopias = QSpinBox()
        self.campoCopias.setRange(1, 99)
        self.campoCopias.setValue(copias)

        if genero:
            self.campoGenero.setCurrentText(genero)

        self.campoSinopse = QPlainTextEdit(sinopse)
        self.campoSinopse.setPlaceholderText("Resumo do filme, sem revelar o final")

        self.botaoSalvar = QPushButton("Salvar")
        self.botaoSalvar.clicked.connect(self.accept)

        layout = QFormLayout()
        layout.addRow("Título:", self.campoTitulo)
        layout.addRow("Gênero:", self.campoGenero)
        layout.addRow("Cópias:", self.campoCopias)
        layout.addRow("Sinopse:", self.campoSinopse)
        layout.addRow(self.botaoSalvar)
        self.setLayout(layout)

    def closeEvent(self, event):
        print("Janela de cadastro fechada")
        event.accept()


class JanelaHistorico(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Histórico de Aluguéis")
        self.resize(500, 400)

        self.textoHistorico = QLabel("Carregando...")
        self.lista = QListWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.textoHistorico)
        layout.addWidget(self.lista)
        self.setLayout(layout)

    def preencher(self, registros):
        self.lista.clear()
        for r in registros:
            self.lista.addItem(f"{r['data_hora']} - {r['usuario']} - {r['filme']} - {r['acao']}")
        self.textoHistorico.setText(f"{len(registros)} registro(s)")


class JanelaCadastroUsuario(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Criar conta")
        self.resize(420, 520)
        self.setObjectName("raiz")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(tema.estilo_login())

        icone = QLabel("👤")
        icone.setAlignment(Qt.AlignCenter)
        fonteIcone = QFont()
        fonteIcone.setPointSize(40)
        icone.setFont(fonteIcone)

        titulo = QLabel("Criar conta")
        titulo.setAlignment(Qt.AlignCenter)
        fonteTitulo = QFont()
        fonteTitulo.setPointSize(20)
        fonteTitulo.setBold(True)
        titulo.setFont(fonteTitulo)

        self.login = QLineEdit()
        self.login.setPlaceholderText("Login")

        self.senha = QLineEdit()
        self.senha.setPlaceholderText("Senha")
        self.senha.setEchoMode(QLineEdit.Password)

        self.confirmarSenha = QLineEdit()
        self.confirmarSenha.setPlaceholderText("Confirmar senha")
        self.confirmarSenha.setEchoMode(QLineEdit.Password)

        self.verSenha = QCheckBox("Mostrar senha")
        self.verSenha.toggled.connect(self.alternar_senha)

        self.salvar = QPushButton("Criar conta")
        self.salvar.setObjectName("botaoLogin")
        self.salvar.setCursor(Qt.PointingHandCursor)
        self.salvar.clicked.connect(self.accept)

        self.cancelar = QPushButton("Cancelar")
        self.cancelar.setObjectName("botaoCriar")
        self.cancelar.setCursor(Qt.PointingHandCursor)
        self.cancelar.clicked.connect(self.reject)

        cartao = QWidget()
        cartao.setFixedWidth(320)
        coluna = QVBoxLayout(cartao)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(12)
        coluna.addWidget(icone)
        coluna.addWidget(titulo)
        coluna.addSpacing(16)
        coluna.addWidget(self.login)
        coluna.addWidget(self.senha)
        coluna.addWidget(self.confirmarSenha)
        coluna.addWidget(self.verSenha)
        coluna.addSpacing(4)
        coluna.addWidget(self.salvar)
        coluna.addWidget(self.cancelar)

        raiz = QVBoxLayout(self)
        raiz.addStretch()
        raiz.addWidget(cartao, alignment=Qt.AlignHCenter)
        raiz.addStretch()

    def alternar_senha(self, visivel):
        modo = QLineEdit.Normal if visivel else QLineEdit.Password
        self.senha.setEchoMode(modo)
        self.confirmarSenha.setEchoMode(modo)


class EstrelasWidget(QWidget):
    mudou = Signal(int)

    def __init__(self, valor=5):
        super().__init__()
        self._valor = valor
        self._botoes = []
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        for i in range(1, 6):
            botao = QPushButton("★")
            botao.setFlat(True)
            botao.setCursor(Qt.PointingHandCursor)
            botao.setToolTip(f"{i} de 5")
            botao.clicked.connect(lambda _=False, n=i: self.setValue(n))
            layout.addWidget(botao)
            self._botoes.append(botao)
        layout.addStretch()
        self.setValue(valor)

    def value(self):
        return self._valor

    def setValue(self, valor):
        self._valor = valor
        for i, botao in enumerate(self._botoes, 1):
            cor = "#f5b301" if i <= valor else "#8a8a8a"
            botao.setStyleSheet(
                f"border: none; background: transparent; font-size: 32px; color: {cor};")
        self.mudou.emit(valor)


class JanelaAvaliar(QDialog):
    def __init__(self, titulo_filme, nota=5, comentario=""):
        super().__init__()
        self.setWindowTitle("Avaliar Filme")
        self.resize(380, 300)

        self.campoFilme = QLineEdit(titulo_filme)
        self.campoFilme.setEnabled(False)

        self.campoNota = EstrelasWidget(nota)

        self.campoComentario = QPlainTextEdit(comentario)
        self.campoComentario.setPlaceholderText("Comentário (opcional)")

        self.botaoSalvar = QPushButton("Salvar avaliação")
        self.botaoSalvar.clicked.connect(self.accept)

        layout = QFormLayout()
        layout.addRow("Filme:", self.campoFilme)
        layout.addRow("Nota:", self.campoNota)
        layout.addRow("Comentário:", self.campoComentario)
        layout.addRow(self.botaoSalvar)
        self.setLayout(layout)