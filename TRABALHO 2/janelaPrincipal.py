import sys
from PySide6.QtWidgets import (
    QWidget, QApplication, QMainWindow, QToolBar, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QListWidget, QListWidgetItem, QDialog,
    QFormLayout, QComboBox, QMessageBox, QFormLayout, QComboBox, QMessageBox, QFileDialog, QStyle
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from models import Filme, ALUGADO, DISPONIVEL
from repositorio import RepositorioFilmes
from historicoAlgueis import historico
from dialogos import JanelaAlugar, JanelaCadastro, JanelaHistorico
from tarefas_arquivo import GravarDados, CarregarHistorico, ExportarHistorico
import tema

class Janela(QMainWindow):
    def __init__(self, login,tipo_usuario="Usuário"):
        super().__init__()
        self.tipo_usuario = tipo_usuario
        self.login = login
        self.setWindowTitle(f"Locadora - {tipo_usuario}")
        self.resize(800, 600)

        self.repositorio = RepositorioFilmes()
        self.historico = historico()
        self.filmes = self.repositorio.carregar()
        self.tarefas = []

        self.menuGenero = self.menuBar().addMenu("Gênero")
        for genero in ["romance", "ação", "drama", "terror", "ficção científica"]:
            acao = QAction(genero, self)
            acao.triggered.connect(lambda checked, g=genero: self.filtrar_por_genero(g))
            self.menuGenero.addAction(acao)


        self.menuFilme = self.menuBar().addMenu("Filme")
        self.barra = QToolBar()
        self.barra.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(self.barra)

        if self.tipo_usuario == "Admin":
            self.acaoCadastrar = QAction("Cadastrar Filme", self)
            self.acaoEditar = QAction("Editar Filme", self)
            self.acaoExcluir = QAction("Excluir Filme", self)

            self.acaoCadastrar.setShortcut("Ctrl+N")
            self.acaoEditar.setShortcut("Ctrl+E")

            self.acaoCadastrar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
            self.acaoEditar.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            self.acaoExcluir.setIcon(self.style().standardIcon(QStyle.SP_TrashIcon))

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
            self.acaoAlugar.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.acaoDevolver.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))
            self.acaoDevolver.triggered.connect(self.devolver_filme)

            self.acaoAlugar.setShortcut("Ctrl+R")
            self.acaoDevolver.setShortcut("Ctrl+D")

            self.menuFilme.addAction(self.acaoAlugar)
            self.menuFilme.addAction(self.acaoDevolver)

            self.barra.addAction(self.acaoAlugar)
            self.barra.addAction(self.acaoDevolver)

        self.acaoHistorico = QAction("Ver Histórico", self)
        self.acaoHistorico.setShortcut("Ctrl+H")
        self.acaoHistorico.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        self.acaoHistorico.triggered.connect(self.abrir_historico)
        self.menuFilme.addAction(self.acaoHistorico)
        self.barra.addAction(self.acaoHistorico)

        if self.tipo_usuario == "Admin":
            self.acaoExportar = QAction("Exportar Histórico", self)
            self.acaoExportar.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
            self.acaoExportar.setShortcut("Ctrl+S")
            self.acaoExportar.triggered.connect(self.exportar_historico)
            self.menuFilme.addAction(self.acaoExportar)
            self.barra.addAction(self.acaoExportar)

        self.acaoTema = QAction("Alternar tema (claro/escuro)", self)
        self.acaoTema.setIcon(self.style().standardIcon(QStyle.SP_DesktopIcon))
        self.acaoTema.setShortcut("Ctrl+T")
        self.acaoTema.triggered.connect(tema.alternar_tema)
        self.menuFilme.addAction(self.acaoTema)
        self.barra.addAction(self.acaoTema)

        self.acaoSair = QAction("Sair da conta", self)
        self.acaoSair.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
        self.acaoSair.setShortcut("Ctrl+L")
        self.acaoSair.triggered.connect(self.sair_da_conta)
        self.menuFilme.addAction(self.acaoSair)
        self.barra.addAction(self.acaoSair)

        self.acaoAtalhos = QAction("Atalhos", self)
        self.acaoAtalhos.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxQuestion))
        self.acaoAtalhos.setShortcut("F1")
        self.acaoAtalhos.triggered.connect(self.mostrar_atalhos)
        self.menuFilme.addAction(self.acaoAtalhos)
        self.barra.addAction(self.acaoAtalhos)

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
            self.salvar_em_segundo_plano()
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
            self.salvar_em_segundo_plano() 
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
            self.salvar_em_segundo_plano() 
            self.atualizar_lista()

    def abrir_alugar(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para alugar.")
            return

        if not filme.disponivel:
            QMessageBox.warning(self, "Indisponível", f"'{filme.titulo}' já está alugado.")
            return

        dialog = JanelaAlugar(filme.titulo, filme.genero)
        if dialog.exec() == QDialog.Accepted:
            filme.status = ALUGADO
            self.salvar_em_segundo_plano((self.login, filme.titulo, "Aluguel"))
            self.atualizar_lista()
            QMessageBox.information(self, "Sucesso", f"'{filme.titulo}' alugado com sucesso!")

    def devolver_filme(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para devolver.")
            return

        if filme.disponivel:
            QMessageBox.warning(self, "Aviso", f"'{filme.titulo}' não está alugado.")
            return

        resposta = QMessageBox.question(self, "Confirmar devolução", f"Devolver '{filme.titulo}'?")
        if resposta == QMessageBox.Yes:
            filme.status = DISPONIVEL
            self.salvar_em_segundo_plano((self.login, filme.titulo, "Devolução"))
            self.atualizar_lista()
            QMessageBox.information(self, "Sucesso", f"'{filme.titulo}' devolvido com sucesso!")

    def closeEvent(self, event):
        resposta = QMessageBox.question(self, "Sair", "Deseja realmente sair da locadora?")
        if resposta == QMessageBox.Yes:
            for t in list(self.tarefas):
                t.wait()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.tipo_usuario == "Admin":
            self.excluir_filme()

    def salvar_em_segundo_plano(self, registro=None):
        tarefa = GravarDados(self.repositorio, self.filmes, self.historico, registro)
        tarefa.erro.connect(lambda msg: QMessageBox.critical(self, "Erro ao salvar", msg))
        tarefa.finished.connect(lambda t=tarefa: self.tarefas.remove(t) if t in self.tarefas else None)
        self.tarefas.append(tarefa)
        tarefa.start()
        
    def abrir_historico(self):
        self.dialogHistorico = JanelaHistorico()
        tarefa = CarregarHistorico(self.historico)
        tarefa.carregado.connect(self.mostrar_historico)
        tarefa.finished.connect(lambda t=tarefa: self.tarefas.remove(t) if t in self.tarefas else None)
        self.tarefas.append(tarefa)
        tarefa.start()
        self.dialogHistorico.exec()

    def mostrar_historico(self, registros):
        if self.tipo_usuario != "Admin":
            registros = [r for r in registros if r["usuario"] == self.login]
        self.dialogHistorico.preencher(registros)

    def exportar_historico(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Exportar histórico", "historico.txt", "Arquivos de texto (*.txt)"
        )
        if not caminho:
            return
        tarefa = ExportarHistorico(self.historico.carregar(), caminho)
        tarefa.exportado.connect(self.exportacao_concluida)
        tarefa.erro.connect(self.exportacao_erro)
        tarefa.finished.connect(self.exportacao_finalizada)
        self.tarefas.append(tarefa)
        tarefa.start()

    def exportacao_concluida(self, caminho):
        QMessageBox.information(self, "Sucesso", f"Histórico exportado em:\n{caminho}")

    def exportacao_erro(self, mensagem):
        QMessageBox.critical(self, "Erro ao exportar", mensagem)

    def exportacao_finalizada(self):
        tarefa = self.sender()
        if tarefa in self.tarefas:
            self.tarefas.remove(tarefa)

    def sair_da_conta(self):
        from janelaLogin import JanelaLogin
        self.janelaLogin = JanelaLogin()
        self.janelaLogin.show()
        if not self.close():
            self.janelaLogin.close()

    def mostrar_atalhos(self):
        if self.tipo_usuario == "Admin":
            texto = (
                "Ctrl+N  -  Cadastrar filme\n"
                "Ctrl+E  -  Editar filme\n"
                "Delete  -  Excluir filme\n"
                "Ctrl+S  -  Exportar histórico\n"
            )
        else:
            texto = (
                "Ctrl+R  -  Alugar filme\n"
                "Ctrl+D  -  Devolver filme\n"
            )
        texto += (
            "Ctrl+H  -  Ver histórico\n"
            "Ctrl+T  -  Alternar tema claro/escuro\n"
            "Ctrl+L  -  Sair da conta\n"
            "F1  -  Mostrar esta lista"
        )
        QMessageBox.information(self, "Atalhos de teclado", texto)