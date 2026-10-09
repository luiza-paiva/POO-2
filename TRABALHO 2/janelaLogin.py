import sys
from PySide6.QtWidgets import (
    QWidget, QApplication, QMainWindow, QToolBar, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QListWidget, QListWidgetItem, QDialog,
    QFormLayout, QComboBox, QMessageBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from models import Filme
from repositorio import RepositorioFilmes
from janelaPrincipal import Janela

class JanelaLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(350, 200)

        self.campoLogin = QLineEdit()
        self.campoLogin.setPlaceholderText("Login")

        self.campoSenha = QLineEdit()
        self.campoSenha.setPlaceholderText("Senha")
        self.campoSenha.setEchoMode(QLineEdit.Password)

        self.campoTipo = QComboBox()
        self.campoTipo.addItems(["Usuário", "Admin"])

        self.botaoLogin = QPushButton("Entrar")
        self.botaoLogin.clicked.connect(self.fazer_login)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.campoLogin)
        self.layout.addWidget(self.campoSenha)
        self.layout.addWidget(self.campoTipo)
        self.layout.addWidget(self.botaoLogin)
        self.layout.addStretch()

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def fazer_login(self):
        login = self.campoLogin.text().strip()
        senha = self.campoSenha.text().strip()

        if not login or not senha:
            QMessageBox.warning(self, "Aviso", "Preencha login e senha.")
            return

        tipo = self.campoTipo.currentText()
        self.janelaPrincipal = Janela(login, tipo)
        self.janelaPrincipal.show()
        self.close()
