from string import Template

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

ESTILO = Template("""
QWidget#raiz {
    background: $fundo;
}
QLabel {
    color: $texto;
}
QLineEdit {
    background: $campo;
    color: $texto;
    border: 1px solid $borda;
    border-radius: 8px;
    padding: 10px 12px;
}
QLineEdit:focus {
    border: 1px solid $destaque;
}
QCheckBox {
    color: $texto;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid $borda;
    border-radius: 4px;
    background: $campo;
}
QCheckBox::indicator:checked {
    background: $destaque;
    border: 1px solid $destaque;
}
QPushButton#botaoLogin {
    background: $destaque;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 12px;
    font-weight: bold;
}
QPushButton#botaoCriar {
    background: transparent;
    color: $texto;
    border: 1px solid $borda;
    border-radius: 8px;
    padding: 12px;
}
QPushButton#botaoCriar:hover, QPushButton#botaoTema:hover {
    background: $hover;
}
QPushButton#botaoTema {
    background: transparent;
    color: $texto;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
}
""")

CORES_CLARO = {
    "fundo": "#f5f5f5", "campo": "#ffffff", "texto": "#1a1a1a",
    "suave": "#6b7280", "borda": "#c4c4c4", "destaque": "#2a82da",
    "hover": "rgba(0, 0, 0, 20)",
}
CORES_ESCURO = {
    "fundo": "#2d2d2d", "campo": "#1e1e1e", "texto": "#e6e6e6",
    "suave": "#9aa0a6", "borda": "#5a5a5a", "destaque": "#2a82da",
    "hover": "rgba(255, 255, 255, 30)",
}


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
        cores = CORES_ESCURO if tema.carregar_preferencia() else CORES_CLARO
        self.container.setStyleSheet(ESTILO.substitute(cores))

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

        tipo = self.registroUsuarios.validar(login, senha)
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
        if not self.registroUsuarios.cadastrar(login, senha, "Usuário"):
            QMessageBox.warning(self, "Aviso", "Esse login já existe.")
            return

        QMessageBox.information(self, "Sucesso", "Conta criada. Faça login.")