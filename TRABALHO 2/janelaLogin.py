from PySide6.QtWidgets import (
    QWidget, QMainWindow, QLineEdit, QPushButton, QVBoxLayout,
    QDialog, QMessageBox, QComboBox
)
from janelaPrincipal import Janela
from dialogos import JanelaCadastroUsuario
from registroUsuarios import registroUsuarios

class JanelaLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(350, 200)

        self.login = QLineEdit()
        self.login.setPlaceholderText("Login")

        self.senha = QLineEdit()
        self.senha.setPlaceholderText("Senha")
        self.senha.setEchoMode(QLineEdit.Password)
        self.senha.returnPressed.connect(self.fazer_login)

        self.botaoLogin = QPushButton("Login")
        self.botaoLogin.clicked.connect(self.fazer_login)

        self.cadastrar = QPushButton("Criar conta")
        self.cadastrar.clicked.connect(self.cadastrar_usuario)

        #self.tipo = QComboBox()
        #self.tipo.addItems(["Usuário", "Admin"])

        #self.login = QPushButton("Entrar")
        #self.login.clicked.connect(self.fazer_login)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.login)
        self.layout.addWidget(self.senha)
        self.layout.addWidget(self.botaoLogin)
        self.layout.addWidget(self.cadastrar)
        self.layout.addStretch()

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def fazer_login(self):
        login = self.login.text().strip()
        senha = self.senha.text().strip()

        if not login or not senha:
            QMessageBox.warning(self, "Aviso", "Preencha login e senha.")
            return

        tipo = self.repositorioUsuarios.validar(login, senha)
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

        login = self.login.text().strip()
        senha = self.senha.text().strip()
        confirmar = self.confirmar.text().strip()

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
