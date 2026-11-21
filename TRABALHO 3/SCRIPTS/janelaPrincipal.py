from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QToolBar, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QButtonGroup,
    QMessageBox, QFileDialog, QStyle, QScrollArea
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt
from models import Filme, Avaliacao, ALUGADO, DISPONIVEL, GENEROS
from repositorio import RepositorioFilmes, RepositorioAvaliacoes
from historicoAlgueis import historico
from dialogos import JanelaAlugar, JanelaCadastro, JanelaHistorico, JanelaAvaliar
from tarefas_arquivo import GravarDados, CarregarHistorico, ExportarHistorico, GravarAvaliacoes
import tema
from cartaoFilme import FileiraGenero
from telaFilme import TelaFilme

class Janela(QMainWindow):
    def __init__(self, login,tipo_usuario="Usuário"):
        super().__init__()
        self.tipo_usuario = tipo_usuario
        self.login = login
        self.setWindowTitle(f"Locadora - {tipo_usuario}")
        self.resize(1020, 700)
        self.setMinimumSize(760, 520)

        self.repositorio = RepositorioFilmes()
        self.historico = historico()
        self.filmes = self.repositorio.carregar()
        self.repoAvaliacoes = RepositorioAvaliacoes()
        self.avaliacoes = self.repoAvaliacoes.carregar()
        self.tarefas = []

        self.menuGenero = self.menuBar().addMenu("Gênero")
        acaoTodos = QAction("Todos os gêneros", self)
        acaoTodos.triggered.connect(lambda: self.definir_genero(None))
        self.menuGenero.addAction(acaoTodos)
        for genero in GENEROS:
            acao = QAction(genero, self)
            acao.triggered.connect(lambda checked, g=genero: self.filtrar_por_genero(g))
            self.menuGenero.addAction(acao)


        self.menuFilme = self.menuBar().addMenu("Filme")
        self.barra = QToolBar()
        self.barra.setMovable(False)
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

            self.acaoAvaliar = QAction("Avaliar Filme", self)
            self.acaoAvaliar.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))
            self.acaoAvaliar.setShortcut("Ctrl+B")
            self.acaoAvaliar.triggered.connect(self.avaliar_filme)

            self.acaoAlugar.setShortcut("Ctrl+R")
            self.acaoDevolver.setShortcut("Ctrl+D")

            self.menuFilme.addAction(self.acaoAlugar)
            self.menuFilme.addAction(self.acaoDevolver)
            self.menuFilme.addAction(self.acaoAvaliar)

            self.barra.addAction(self.acaoAlugar)
            self.barra.addAction(self.acaoDevolver)
            self.barra.addAction(self.acaoAvaliar)

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

        self.filmeAtual = None
        self.fileiras = []
        self.generoAtivo = None

        saudacao = QLabel(f"Olá, {self.login}")
        saudacao.setObjectName("saudacao")
        if self.tipo_usuario == "Admin":
            dica = "Clique em um filme para ver os detalhes, editar ou excluir."
        else:
            dica = "Clique em um filme para ver a sinopse, alugar ou avaliar."
        subtitulo = QLabel(dica)
        subtitulo.setObjectName("subtitulo")
        textos = QVBoxLayout()
        textos.setSpacing(2)
        textos.addWidget(saudacao)
        textos.addWidget(subtitulo)

        self.input = QLineEdit()
        self.input.setObjectName("busca")
        self.input.setPlaceholderText("Buscar filme pelo nome")
        self.input.setClearButtonEnabled(True)
        self.input.setMinimumWidth(300)
        self.input.textChanged.connect(self.atualizar_lista)

        cabecalho = QHBoxLayout()
        cabecalho.addLayout(textos)
        cabecalho.addStretch()
        cabecalho.addWidget(self.input, alignment=Qt.AlignVCenter)

        self.chips = {}
        grupo = QButtonGroup(self)
        linhaChips = QHBoxLayout()
        linhaChips.setSpacing(8)
        for g in [None] + GENEROS:
            chip = QPushButton("Todos" if g is None else g.capitalize())
            chip.setObjectName("chipGenero")
            chip.setCheckable(True)
            chip.setCursor(Qt.PointingHandCursor)
            chip.clicked.connect(lambda _=False, genero=g: self.definir_genero(genero))
            grupo.addButton(chip)
            linhaChips.addWidget(chip)
            self.chips[g] = chip
        linhaChips.addStretch()
        self.chips[None].setChecked(True)

        self.area = QScrollArea()
        self.area.setWidgetResizable(True)
        self.area.setFrameShape(QScrollArea.NoFrame)
        self.conteudoFileiras = QWidget()
        self.conteudoFileiras.setAutoFillBackground(False)
        self.layoutFileiras = QVBoxLayout(self.conteudoFileiras)
        self.layoutFileiras.setContentsMargins(0, 4, 8, 12)
        self.layoutFileiras.setSpacing(18)
        self.area.setWidget(self.conteudoFileiras)
        self.area.viewport().setAutoFillBackground(False)

        self.layoutPrincipal = QVBoxLayout()
        self.layoutPrincipal.setContentsMargins(28, 22, 20, 8)
        self.layoutPrincipal.setSpacing(16)
        self.layoutPrincipal.addLayout(cabecalho)
        self.layoutPrincipal.addLayout(linhaChips)
        self.layoutPrincipal.addWidget(self.area)

        container = QWidget()
        container.setLayout(self.layoutPrincipal)
        self.setCentralWidget(container)

        self.atualizar_lista()

    def atualizar_lista(self, *_):
        texto = self.input.text().strip().lower()
        filmes = [f for f in self.filmes
                  if (self.generoAtivo is None or f.genero == self.generoAtivo)
                  and texto in f.titulo.lower()]

        while self.layoutFileiras.count():
            item = self.layoutFileiras.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
        self.fileiras = []

        notas = {}
        for a in self.avaliacoes:
            notas.setdefault(a.filme_id, []).append(a.nota)
        resumo = {fid: (sum(v) / len(v), len(v)) for fid, v in notas.items()}

        grupos = {}
        for f in filmes:
            grupos.setdefault(f.genero, []).append(f)
        ordem = [g for g in GENEROS if g in grupos] + [g for g in grupos if g not in GENEROS]

        for genero in ordem:
            fileira = FileiraGenero(genero, grupos[genero], resumo)
            fileira.clicado.connect(self.selecionar_filme)
            self.layoutFileiras.addWidget(fileira)
            self.fileiras.append(fileira)

        if not filmes:
            vazio = QLabel("Nenhum filme encontrado.\nTente outro nome ou escolha “Todos” nos gêneros.")
            vazio.setObjectName("vazio")
            vazio.setAlignment(Qt.AlignCenter)
            self.layoutFileiras.addSpacing(60)
            self.layoutFileiras.addWidget(vazio)

        self.layoutFileiras.addStretch()

        if self.filmeAtual is not None:
            for fileira in self.fileiras:
                for c in fileira.cartoes:
                    c.set_selecionado(c.filme_id == self.filmeAtual.id)

    def definir_genero(self, genero):
        self.generoAtivo = genero
        self.chips[genero].setChecked(True)
        self.atualizar_lista()

    def filtrar_por_genero(self, genero):
        self.definir_genero(genero)

    def filme_selecionado(self):
        return self.filmeAtual

    def selecionar_filme(self, id_filme):
        self.filmeAtual = next((f for f in self.filmes if f.id == id_filme), None)
        for fileira in self.fileiras:
            for c in fileira.cartoes:
                c.set_selecionado(c.filme_id == id_filme)
        if self.filmeAtual is not None:
            TelaFilme(self, self.filmeAtual).exec()

    def ja_alugou(self, filme):
        return any(
            r["usuario"] == self.login and r["filme"] == filme.titulo and r["acao"] == "Aluguel"
            for r in self.historico.carregar()
        )

    def cadastrar_filme(self):
        dialog = JanelaCadastro()
        if dialog.exec() == QDialog.Accepted:
            titulo = dialog.campoTitulo.text().strip()
            genero = dialog.campoGenero.currentText()
            if not titulo:
                QMessageBox.warning(self, "Aviso", "Digite um título.")
                return
            sinopse = dialog.campoSinopse.toPlainText().strip()
            self.filmes.append(Filme(titulo, genero, sinopse=sinopse))
            self.salvar_em_segundo_plano()
            self.atualizar_lista()

    def editar_filme(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para editar.")
            return

        dialog = JanelaCadastro(filme.titulo, filme.genero, filme.sinopse)
        if dialog.exec() == QDialog.Accepted:
            novo_titulo = dialog.campoTitulo.text().strip()
            novo_genero = dialog.campoGenero.currentText()
            if not novo_titulo:
                QMessageBox.warning(self, "Aviso", "Digite um título.")
                return
            filme.titulo = novo_titulo
            filme.genero = novo_genero
            filme.sinopse = dialog.campoSinopse.toPlainText().strip()
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
            self.filmeAtual = None
            self.avaliacoes = [a for a in self.avaliacoes if a.filme_id != filme.id]
            self.salvar_avaliacoes_em_segundo_plano()
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
            filme.alugado_por = self.login
            filme.data_aluguel = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
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

        if filme.alugado_por and filme.alugado_por != self.login:
            QMessageBox.warning(self, "Não permitido",
                                f"'{filme.titulo}' foi alugado por outro usuário.")
            return

        resposta = QMessageBox.question(self, "Confirmar devolução", f"Devolver '{filme.titulo}'?")
        if resposta == QMessageBox.Yes:
            filme.status = DISPONIVEL
            filme.alugado_por = ""
            filme.data_aluguel = ""
            self.salvar_em_segundo_plano((self.login, filme.titulo, "Devolução"))
            self.atualizar_lista()
            QMessageBox.information(self, "Sucesso", f"'{filme.titulo}' devolvido com sucesso!")

    def avaliar_filme(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para avaliar.")
            return


        if not self.ja_alugou(filme):
            QMessageBox.warning(self, "Não permitido", "Você só pode avaliar filmes que já alugou.")
            return

        existente = next((a for a in self.avaliacoes
                          if a.filme_id == filme.id and a.usuario == self.login), None)

        dialog = JanelaAvaliar(filme.titulo,
                               existente.nota if existente else 5,
                               existente.comentario if existente else "")
        if dialog.exec() != QDialog.Accepted:
            return

        nota = dialog.campoNota.value()
        comentario = dialog.campoComentario.toPlainText().strip()
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if existente: 
            existente.nota = nota
            existente.comentario = comentario
            existente.data_hora = agora
        else:
            self.avaliacoes.append(Avaliacao(filme.id, self.login, nota, comentario, agora))

        self.salvar_avaliacoes_em_segundo_plano()
        self.atualizar_lista()

    def salvar_avaliacoes_em_segundo_plano(self):
        tarefa = GravarAvaliacoes(self.repoAvaliacoes, self.avaliacoes)
        tarefa.erro.connect(lambda msg: QMessageBox.critical(self, "Erro ao salvar", msg))
        tarefa.finished.connect(lambda t=tarefa: self.tarefas.remove(t) if t in self.tarefas else None)
        self.tarefas.append(tarefa)
        tarefa.start()

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
                "Ctrl+B  -  Avaliar filme\n"
            )
        texto += (
            "Ctrl+H  -  Ver histórico\n"
            "Ctrl+T  -  Alternar tema claro/escuro\n"
            "Ctrl+L  -  Sair da conta\n"
            "F1  -  Mostrar esta lista"
        )
        QMessageBox.information(self, "Atalhos de teclado", texto)