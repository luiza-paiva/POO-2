from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QLineEdit, QPushButton, QVBoxLayout,
    QLabel, QCheckBox, QDialog, QMessageBox
)
from janelaPrincipal import Janela
from dialogos import JanelaCadastroUsuario
from registroUsuarios import registroUsuarios
import tema
import clienteApi

class JanelaLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Locadora de Filmes")
        self.resize(420, 560)
        self.setMinimumSize(380, 520)
        self.registroUsuarios = registroUsuarios(None)

        icone = QLabel("🎬")
        icone.setAlignment(Qt.AlignCenter)
        fonte_icone = QFont()
        fonte_icone.setPointSize(40)
        icone.setFont(fonte_icone)

        titulo = QLabel("Locadora de Filmes")
        titulo.setAlignment(Qt.AlignCenter)
        fonte_titulo = QFont()
        fonte_titulo.setPointSize(20)
        fonte_titulo.setBold(True)
        titulo.setFont(fonte_titulo)

        self.login = QLineEdit()
        self.login.setPlaceholderText("Login")
        self.login.returnPressed.connect(lambda: self.senha.setFocus())

        self.senha = QLineEdit()
        self.senha.setPlaceholderText("Senha")
        self.senha.setEchoMode(QLineEdit.Password)
        self.senha.returnPressed.connect(self.fazer_login)

        self.verSenha = QCheckBox("Mostrar senha")
        self.verSenha.toggled.connect(self.alternar_senha)

        self.botaoLogin = QPushButton("Entrar")
        self.botaoLogin.setObjectName("botaoLogin")
        self.botaoLogin.setCursor(Qt.PointingHandCursor)
        self.botaoLogin.clicked.connect(self.fazer_login)

        self.cadastrar = QPushButton("Criar conta")
        self.cadastrar.setObjectName("botaoCriar")
        self.cadastrar.setCursor(Qt.PointingHandCursor)
        self.cadastrar.clicked.connect(self.cadastrar_usuario)

        self.botaoTema = QPushButton("🌓 Alternar tema")
        self.botaoTema.setObjectName("botaoTema")
        self.botaoTema.setCursor(Qt.PointingHandCursor)
        self.botaoTema.clicked.connect(self.alternar_tema)

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
        coluna.addWidget(self.verSenha)
        coluna.addSpacing(4)
        coluna.addWidget(self.botaoLogin)
        coluna.addWidget(self.cadastrar)
        coluna.addSpacing(8)
        coluna.addWidget(self.botaoTema, alignment=Qt.AlignHCenter)

        raiz = QVBoxLayout()
        raiz.addStretch()
        raiz.addWidget(cartao, alignment=Qt.AlignHCenter)
        raiz.addStretch()

        self.container = QWidget()
        self.container.setObjectName("raiz")
        self.container.setLayout(raiz)
        self.setCentralWidget(self.container)
        self.aplicar_estilo()

    def aplicar_estilo(self):
        self.container.setStyleSheet(tema.estilo_login())

    def alternar_tema(self):
        tema.alternar_tema()
        self.aplicar_estilo()

    def alternar_senha(self, visivel):
        self.senha.setEchoMode(QLineEdit.Normal if visivel else QLineEdit.Password)

    def fazer_login(self):
        login = self.login.text().strip()
        senha = self.senha.text().strip()

        if not login or not senha:
            QMessageBox.warning(self, "Aviso", "Preencha login e senha.")
            return

        try:
            tipo = clienteApi.login(login, senha)
        except clienteApi.ErroApi as erro:
            QMessageBox.critical(self, "Erro", str(erro))
            return

        if tipo is None:
            QMessageBox.warning(self, "Erro", "Login ou senha inválidos.")
            return

        self.janelaPrincipal = Janela(login, tipo)
        self.janelaPrincipal.show()
        self.close()

    def cadastrar_usuario(self):
        dialogo = JanelaCadastroUsuario()
        if dialogo.exec() != QDialog.Accepted:
            return

        login = dialogo.login.text().strip()
        senha = dialogo.senha.text().strip()
        confirmar = dialogo.confirmarSenha.text().strip()

        if not login or not senha:
            QMessageBox.warning(self, "Aviso", "Preencha login e senha.")
            return
        elif senha != confirmar:
            QMessageBox.warning(self, "Aviso", "As senhas não conferem.")
            return
        try:
            criou = clienteApi.cadastrar(login, senha)
        except clienteApi.ErroApi as erro:
            QMessageBox.critical(self, "Erro", str(erro))
            return
        if not criou:
            QMessageBox.warning(self, "Aviso", "Esse login já existe.")
            return

        QMessageBox.information(self, "Sucesso", "Conta criada. Faça login.")