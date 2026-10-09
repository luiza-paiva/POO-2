# locadora de filme
# sinais e slots
# eventos
# diversos tipos de widgets
# layouts
# barras de ferramentas menu
# dialogs/alerts
# pelo menos uma janela adicional

import sys
from PySide6.QtWidgets import (
    QWidget, QApplication, QMainWindow, QToolBar, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QListWidget, QDialog, QFormLayout,
    QComboBox, QMessageBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
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


class Janela(QMainWindow):
    def __init__(self, tipo_usuario="Usuário"):
        super().__init__()
        self.tipo_usuario = tipo_usuario
        self.setWindowTitle(f"Locadora - {tipo_usuario}")
        self.resize(800, 600)


        self.filmes = [
            ["O Poderoso Chefão", "drama", "Disponível"],
            ["Pânico", "terror", "Disponível"],
            ["Duna", "ficção científica", "Disponível"],
            ["Titanic", "romance", "Disponível"],
            ["Interestelar", "ficção científica", "Disponível"],
            ["John Wick", "ação", "Disponível"],
            ["Invocação do Mal", "terror", "Disponível"],
            ["Orgulho e Preconceito", "romance", "Disponível"],
            ["Clube da Luta", "drama", "Disponível"],
            ["Mad Max: Estrada da Fúria", "ação", "Disponível"],
            ["Corra!", "terror", "Disponível"],
            ["Blade Runner 2049", "ficção científica", "Disponível"],
            ["Diário de uma Paixão", "romance", "Disponível"],
            ["Cidade de Deus", "drama", "Disponível"],
            ["Um Sonho de Liberdade", "drama", "Disponível"],
        ]


        self.menuGenero = self.menuBar().addMenu("Gênero")
        for genero in ["romance", "ação", "drama", "terror", "ficção científica"]:
            acao = QAction(genero, self)
            acao.triggered.connect(lambda checked, g=genero: self.filtrar_por_genero(g))
            self.menuGenero.addAction(acao)


        self.menuFilme = self.menuBar().addMenu("Filme")
        self.barra = QToolBar()
        self.addToolBar(self.barra)

        if self.tipo_usuario == "Admin":
            self.acaoCadastrar = QAction("Cadastrar Filme", self)
            self.acaoEditar = QAction("Editar Filme", self)
            self.acaoExcluir = QAction("Excluir Filme", self)

            self.acaoCadastrar.triggered.connect(self.cadastrar_filme)
            self.acaoEditar.triggered.connect(self.editar_filme)
            self.acaoExcluir.triggered.connect(self.excluir_filme)

            self.menuFilme.addAction(self.acaoCadastrar)
            self.menuFilme.addAction(self.acaoEditar)
            self.menuFilme.addAction(self.acaoExcluir)

            self.barra.addAction(self.acaoCadastrar)
            self.barra.addAction(self.acaoEditar)
            self.barra.addAction(self.acaoExcluir)


        else:

            self.acaoAlugar = QAction("Alugar Filme", self)
            self.acaoAlugar.triggered.connect(self.abrir_alugar)

            self.acaoDevolver = QAction("Devolver Filme", self)
            self.acaoDevolver.triggered.connect(self.devolver_filme)

            self.menuFilme.addAction(self.acaoAlugar)
            self.menuFilme.addAction(self.acaoDevolver)

            self.barra.addAction(self.acaoAlugar)
            self.barra.addAction(self.acaoDevolver)


        self.input = QLineEdit()
        self.input.setPlaceholderText("Buscar filme...")
        self.input.returnPressed.connect(self.buscar_filme)

        self.botao = QPushButton("Buscar")
        self.botao.clicked.connect(self.buscar_filme)

        self.lista = QListWidget()


        self.textoLocadora = QLabel("Locadora de Filmes")
        self.layoutPrincipal = QVBoxLayout()
        self.layoutPrincipal.addWidget(self.textoLocadora)
        self.layoutPrincipal.addWidget(self.input)
        self.layoutPrincipal.addWidget(self.botao)
        self.layoutPrincipal.addWidget(self.lista)

        container = QWidget()
        container.setLayout(self.layoutPrincipal)
        self.setCentralWidget(container)

        self.atualizar_lista()


    def atualizar_lista(self, filmes=None):
        self.lista.clear()
        for titulo, genero, status in (filmes if filmes is not None else self.filmes):
            self.lista.addItem(f"{titulo} ({genero}) - {status}")

    def filtrar_por_genero(self, genero):
        filtrados = [f for f in self.filmes if f[1] == genero]
        self.atualizar_lista(filtrados)

    def buscar_filme(self):
        texto = self.input.text().lower()
        filtrados = [f for f in self.filmes if texto in f[0].lower()]
        self.atualizar_lista(filtrados)

    def cadastrar_filme(self):
        dialog = JanelaCadastro()
        if dialog.exec() == QDialog.Accepted:
            titulo = dialog.campoTitulo.text().strip()
            genero = dialog.campoGenero.currentText()
            if not titulo:
                QMessageBox.warning(self, "Aviso", "Digite um título.")
                return
            self.filmes.append([titulo, genero, "Disponível"])
            self.atualizar_lista()

    def editar_filme(self):
        item = self.lista.currentItem()
        if item is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para editar.")
            return

        indice = self.lista.currentRow()
        titulo_atual, genero_atual, status_atual = self.filmes[indice]

        dialog = JanelaCadastro(titulo_atual, genero_atual)
        if dialog.exec() == QDialog.Accepted:
            novo_titulo = dialog.campoTitulo.text().strip()
            novo_genero = dialog.campoGenero.currentText()
            if not novo_titulo:
                QMessageBox.warning(self, "Aviso", "Digite um título.")
                return
            self.filmes[indice] = [novo_titulo, novo_genero, status_atual]
            self.atualizar_lista()

    def excluir_filme(self):
        item = self.lista.currentItem()
        if item is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para excluir.")
            return

        indice = self.lista.currentRow()
        titulo, _, _ = self.filmes[indice]

        resposta = QMessageBox.question(
            self, "Confirmar exclusão", f"Excluir '{titulo}'?"
        )
        if resposta == QMessageBox.Yes:
            self.filmes.pop(indice)
            self.atualizar_lista()

    def abrir_alugar(self):
        item = self.lista.currentItem()
        if item is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para alugar.")
            return

        indice = self.lista.currentRow()
        titulo, genero, status = self.filmes[indice]

        if status == "Alugado":
            QMessageBox.warning(self, "Indisponível", f"'{titulo}' já está alugado.")
            return

        dialog = JanelaAlugar(titulo, genero)
        if dialog.exec() == QDialog.Accepted:
            self.filmes[indice][2] = "Alugado"
            self.atualizar_lista()
            QMessageBox.information(self, "Sucesso", f"'{titulo}' alugado com sucesso!")

    def devolver_filme(self):
        item = self.lista.currentItem()
        if item is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para devolver.")
            return

        indice = self.lista.currentRow()
        titulo, genero, status = self.filmes[indice]

        if status == "Disponível":
            QMessageBox.warning(self, "Aviso", f"'{titulo}' não está alugado.")
            return

        resposta = QMessageBox.question(self, "Confirmar devolução", f"Devolver '{titulo}'?")
        if resposta == QMessageBox.Yes:
            self.filmes[indice][2] = "Disponível"
            self.atualizar_lista()
            QMessageBox.information(self, "Sucesso", f"'{titulo}' devolvido com sucesso!")


    def closeEvent(self, event):
        resposta = QMessageBox.question(self, "Sair", "Deseja realmente sair da locadora?")
        if resposta == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.tipo_usuario == "Admin":
            self.excluir_filme()


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
        self.janelaPrincipal = Janela(tipo)
        self.janelaPrincipal.show()
        self.close()


app = QApplication(sys.argv)

janelaLogin = JanelaLogin()
janelaLogin.show()

sys.exit(app.exec())