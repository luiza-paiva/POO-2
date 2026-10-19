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
    def __init__(self, titulo="", genero=""):
        super().__init__()
        self.setWindowTitle("Cadastrar/Editar Filme")
        self.resize(300, 150)

        self.campoTitulo = QLineEdit(titulo)
        self.campoGenero = QComboBox()
        self.campoGenero.addItems(["romance", "ação", "drama", "terror", "ficção científica"])
        if genero:
            self.campoGenero.setCurrentText(genero)

        self.botaoSalvar = QPushButton("Salvar")
        self.botaoSalvar.clicked.connect(self.accept)

        layout = QFormLayout()
        layout.addRow("Título:", self.campoTitulo)
        layout.addRow("Gênero:", self.campoGenero)
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
        self.setWindowTitle("Cadastrar Usuario")
        self.resize(300, 150)

        self.login = QLineEdit()
        self.senha = QLineEdit()
        self.senha.setEchoMode(QLineEdit.Password)
        self.confirmarSenha = QLineEdit()
        self.confirmarSenha.setEchoMode(QLineEdit.Password)

        self.salvar = QPushButton("Salvar")
        self.salvar.clicked.connect(self.accept)

        self.layout = QFormLayout()
        self.layout.addRow("Login:", self.login)
        self.layout.addRow("Senha:", self.senha)
        self.layout.addRow("Confirmar senha:", self.confirmarSenha)
        self.layout.addRow(self.salvar)
        self.setLayout(self.layout)
