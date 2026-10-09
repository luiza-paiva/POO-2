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

class Janela(QMainWindow):
    def __init__(self, tipo_usuario="Usuário"):
        super().__init__()
        self.tipo_usuario = tipo_usuario
        self.setWindowTitle(f"Locadora - {tipo_usuario}")
        self.resize(800, 600)

        self.repositorio = RepositorioFilmes()
        self.filmes = self.repositorio.carregar()

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
        for filme in (filmes if filmes is not None else self.filmes):
            item = QListWidgetItem(str(filme))
            item.setData(Qt.UserRole, filme.id)
            self.lista.addItem(item)

    def filtrar_por_genero(self, genero):
        filtrados = [f for f in self.filmes if f.genero == genero]
        self.atualizar_lista(filtrados)

    def buscar_filme(self):
        texto = self.input.text().lower()
        filtrados = [f for f in self.filmes if texto in f.titulo.lower()]
        self.atualizar_lista(filtrados)

    def filme_selecionado(self):
        item = self.lista.currentItem()
        if item is None:
            return None
        id_selecionado = item.data(Qt.UserRole)
        return next((f for f in self.filmes if f.id == id_selecionado), None)

    def cadastrar_filme(self):
        dialog = JanelaCadastro()
        if dialog.exec() == QDialog.Accepted:
            titulo = dialog.campoTitulo.text().strip()
            genero = dialog.campoGenero.currentText()
            if not titulo:
                QMessageBox.warning(self, "Aviso", "Digite um título.")
                return
            self.filmes.append(Filme(titulo, genero))
            self.repositorio.salvar(self.filmes)
            self.atualizar_lista()

    def editar_filme(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para editar.")
            return

        dialog = JanelaCadastro(filme.titulo, filme.genero)
        if dialog.exec() == QDialog.Accepted:
            novo_titulo = dialog.campoTitulo.text().strip()
            novo_genero = dialog.campoGenero.currentText()
            if not novo_titulo:
                QMessageBox.warning(self, "Aviso", "Digite um título.")
                return
            filme.titulo = novo_titulo
            filme.genero = novo_genero
            self.repositorio.salvar(self.filmes)
            self.atualizar_lista()

    def excluir_filme(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para excluir.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão", f"Excluir '{filme.titulo}'?"
        )
        if resposta == QMessageBox.Yes:
            self.filmes.remove(filme)
            self.repositorio.salvar(self.filmes)
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