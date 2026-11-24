import os
import shutil
from cartaoFilme import FileiraGenero, caminho_poster, PASTA_CACHE, EXTENSOES
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QToolBar, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QButtonGroup,
    QMessageBox, QFileDialog, QStyle, QScrollArea
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QTimer
from models import Filme, GENEROS
from dialogos import JanelaAlugar, JanelaCadastro, JanelaHistorico, JanelaAvaliar
from tarefas_arquivo import ExportarHistorico, BaixarPosters
import tema
from cartaoFilme import FileiraGenero, caminho_poster
from telaFilme import TelaFilme
import clienteApi

INTERVALO_SINCRONIZACAO_MS = 5000


class Janela(QMainWindow):
    def __init__(self, login, tipo_usuario="Usuário"):
        super().__init__()
        self.tipo_usuario = tipo_usuario
        self.login = login
        self.setWindowTitle(f"Locadora - {tipo_usuario}")
        self.resize(1020, 700)
        self.setMinimumSize(760, 520)

        self.filmeAtual = None
        self.fileiras = []
        self.generoAtivo = None
        self.telaFilme = None
        self.tarefas = []
        self._sincronizando = False
        self.idsRecomendados = []

        self.filmes = self.carregar_filmes_da_api() or []
        self.carregar_recomendados()

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
            self.barra.addAction(self.acaoCadastrar)
            self.menuFilme.addAction(self.acaoEditar)
            self.menuFilme.addAction(self.acaoExcluir)

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
        self.baixar_posters()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.sincronizar)
        self.timer.start(INTERVALO_SINCRONIZACAO_MS)

    def enviar_poster(self, filme_id, caminho):
        try:
            clienteApi.enviar_poster(filme_id, caminho)
        except clienteApi.ErroApi as erro:
            QMessageBox.warning(self, "Aviso", f"Filme salvo, mas o pôster não foi enviado: {erro}")
            return
        os.makedirs(PASTA_CACHE, exist_ok=True)
        for ext in EXTENSOES:
            antigo = os.path.join(PASTA_CACHE, filme_id + ext)
            if os.path.exists(antigo):
                os.remove(antigo)
        ext = os.path.splitext(caminho)[1].lower()
        shutil.copyfile(caminho, os.path.join(PASTA_CACHE, filme_id + ext))

    # ------------------------------------------------------------------
    # Lista de filmes
    # ------------------------------------------------------------------
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

        resumo = {f.id: (f.media, f.qtd_avaliacoes) for f in self.filmes if f.qtd_avaliacoes}

        grupos = {}
        for f in filmes:
            grupos.setdefault(f.genero, []).append(f)
        ordem = [g for g in GENEROS if g in grupos] + [g for g in grupos if g not in GENEROS]

        for genero in ordem:
            fileira = FileiraGenero(genero, grupos[genero], resumo)
            fileira.clicado.connect(self.selecionar_filme)
            self.layoutFileiras.addWidget(fileira)
            self.fileiras.append(fileira)

        if self.generoAtivo is None and not texto:
            porId = {f.id: f for f in self.filmes}
            recomendados = [porId[i] for i in self.idsRecomendados if i in porId]
            if recomendados:
                fileira = FileiraGenero("Recomendados para você", recomendados, resumo)
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

    def baixar_posters(self):
        if any(isinstance(t, BaixarPosters) for t in self.tarefas):
            return
        pendentes = [f for f in self.filmes if not caminho_poster(f)]
        if not pendentes:
            return
        tarefa = BaixarPosters(pendentes)
        tarefa.baixado.connect(self.atualizar_lista)
        tarefa.finished.connect(self.exportacao_finalizada)
        self.tarefas.append(tarefa)
        tarefa.start()

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
            self.telaFilme = TelaFilme(self, self.filmeAtual)
            self.telaFilme.exec()
            self.telaFilme = None

    # ------------------------------------------------------------------
    # Comunicação com a API
    # ------------------------------------------------------------------
    def carregar_filmes_da_api(self):
        """Devolve a lista de filmes, ou None se a API falhar."""
        try:
            dados = clienteApi.listar_filmes(self.login)
        except clienteApi.ErroApi as erro:
            QMessageBox.critical(self, "Erro", str(erro))
            return None
        return [Filme.from_dict(d) for d in dados]

    def carregar_recomendados(self):
        """Busca na API os ids dos filmes recomendados (só para usuário comum)."""
        if self.tipo_usuario == "Admin":
            self.idsRecomendados = []
            return
        try:
            dados = clienteApi.listar_recomendados(self.login)
        except clienteApi.ErroApi:
            self.idsRecomendados = []  # silencioso: recomendação é opcional
            return
        self.idsRecomendados = [d["id"] for d in dados]

    def recarregar(self):
        novos = self.carregar_filmes_da_api()
        if novos is None:
            return
        self.filmes = novos
        self.carregar_recomendados()
        if self.filmeAtual is not None:
            self.filmeAtual = next((f for f in self.filmes if f.id == self.filmeAtual.id), None)
        self.atualizar_lista()
        self.baixar_posters()

    def sincronizar(self):
        if self._sincronizando:
            return
        self._sincronizando = True
        try:
            try:
                dados = clienteApi.listar_filmes(self.login)
            except clienteApi.ErroApi:
                return  # silencioso: sem caixa de erro a cada ciclo
            novos = [Filme.from_dict(d) for d in dados]

            antigos_ids = list(self.idsRecomendados)
            self.carregar_recomendados()
            mudou_recomendados = antigos_ids != self.idsRecomendados

            if ([f.to_dict() for f in novos] == [f.to_dict() for f in self.filmes]
                    and not mudou_recomendados):
                return
            self.filmes = novos
            if self.filmeAtual is not None:
                self.filmeAtual = next((f for f in novos if f.id == self.filmeAtual.id), None)
            self.atualizar_lista()
            self.baixar_posters()
            if self.telaFilme is not None:
                if self.filmeAtual is None:
                    self.telaFilme.accept()  # filme excluído por outro usuário
                else:
                    self.telaFilme.atualizar()
        finally:
            self._sincronizando = False

    def ja_alugou(self, filme):
        try:
            registros = clienteApi.historico(self.login)
        except clienteApi.ErroApi:
            return False
        return any(r["filme"] == filme.titulo and r["acao"] == "Aluguel" for r in registros)

    # ------------------------------------------------------------------
    # Ações sobre filmes
    # ------------------------------------------------------------------
    def cadastrar_filme(self):
        dialog = JanelaCadastro()
        if dialog.exec() == QDialog.Accepted:
            titulo = dialog.campoTitulo.text().strip()
            genero = dialog.campoGenero.currentText()
            if not titulo:
                QMessageBox.warning(self, "Aviso", "Digite um título.")
                return
            sinopse = dialog.campoSinopse.toPlainText().strip()
            copias = dialog.campoCopias.value()
            try:
                novo_id = clienteApi.cadastrar_filme(titulo, genero, sinopse, copias)
            except clienteApi.ErroApi as erro:
                QMessageBox.warning(self, "Aviso", str(erro))
                return
            if dialog.caminhoPoster and novo_id:
                self.enviar_poster(novo_id, dialog.caminhoPoster)
            self.recarregar()

    def editar_filme(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para editar.")
            return

        dialog = JanelaCadastro(filme.titulo, filme.genero, filme.sinopse, filme.copias)
        if dialog.exec() == QDialog.Accepted:
            novo_titulo = dialog.campoTitulo.text().strip()
            novo_genero = dialog.campoGenero.currentText()
            if not novo_titulo:
                QMessageBox.warning(self, "Aviso", "Digite um título.")
                return
            sinopse = dialog.campoSinopse.toPlainText().strip()
            copias = dialog.campoCopias.value()
            try:
                clienteApi.editar_filme(filme.id, novo_titulo, novo_genero, sinopse, copias)
            except clienteApi.ErroApi as erro:
                QMessageBox.warning(self, "Aviso", str(erro))
                return
            if dialog.caminhoPoster:
                self.enviar_poster(filme.id, dialog.caminhoPoster)
            self.recarregar()

    def excluir_filme(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para excluir.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar exclusão", f"Excluir '{filme.titulo}'?"
        )
        if resposta == QMessageBox.Yes:
            try:
                clienteApi.excluir_filme(filme.id)
            except clienteApi.ErroApi as erro:
                QMessageBox.warning(self, "Aviso", str(erro))
                return
            self.filmeAtual = None
            self.recarregar()

    def abrir_alugar(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para alugar.")
            return

        if not filme.disponivel:
            QMessageBox.warning(self, "Indisponível", f"'{filme.titulo}' não tem cópias disponíveis.")
            return

        dialog = JanelaAlugar(filme.titulo, filme.genero)
        if dialog.exec() == QDialog.Accepted:
            try:
                clienteApi.alugar(self.login, filme.id)
            except clienteApi.ErroApi as erro:
                QMessageBox.warning(self, "Aviso", str(erro))
                self.recarregar()
                return
            self.recarregar()
            QMessageBox.information(self, "Sucesso", f"'{filme.titulo}' alugado com sucesso!")

    def devolver_filme(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para devolver.")
            return
        if filme.alugado_por != self.login:
            QMessageBox.warning(self, "Aviso", f"Você não alugou '{filme.titulo}'.")
            return

        resposta = QMessageBox.question(self, "Confirmar devolução", f"Devolver '{filme.titulo}'?")
        if resposta == QMessageBox.Yes:
            try:
                clienteApi.devolver(self.login, filme.id)
            except clienteApi.ErroApi as erro:
                QMessageBox.warning(self, "Aviso", str(erro))
                self.recarregar()
                return
            self.recarregar()
            QMessageBox.information(self, "Sucesso", f"'{filme.titulo}' devolvido com sucesso!")

    def avaliar_filme(self):
        filme = self.filme_selecionado()
        if filme is None:
            QMessageBox.warning(self, "Aviso", "Selecione um filme para avaliar.")
            return

        if not self.ja_alugou(filme):
            QMessageBox.warning(self, "Não permitido", "Você só pode avaliar filmes que já alugou.")
            return

        try:
            avaliacoes = clienteApi.listar_avaliacoes(filme.id)
        except clienteApi.ErroApi as erro:
            QMessageBox.critical(self, "Erro", str(erro))
            return
        existente = next((a for a in avaliacoes if a["usuario"] == self.login), None)

        dialog = JanelaAvaliar(filme.titulo,
                               existente["nota"] if existente else 5,
                               existente["comentario"] if existente else "")
        if dialog.exec() != QDialog.Accepted:
            return

        nota = dialog.campoNota.value()
        comentario = dialog.campoComentario.toPlainText().strip()
        try:
            clienteApi.avaliar(self.login, filme.id, nota, comentario)
        except clienteApi.ErroApi as erro:
            QMessageBox.warning(self, "Aviso", str(erro))
            return
        self.recarregar()

    # ------------------------------------------------------------------
    # Histórico
    # ------------------------------------------------------------------
    def abrir_historico(self):
        usuario = None if self.tipo_usuario == "Admin" else self.login
        try:
            registros = clienteApi.historico(usuario)
        except clienteApi.ErroApi as erro:
            QMessageBox.critical(self, "Erro", str(erro))
            return
        self.dialogHistorico = JanelaHistorico()
        self.dialogHistorico.preencher(registros)
        self.dialogHistorico.exec()

    def exportar_historico(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Exportar histórico", "historico.txt", "Arquivos de texto (*.txt)"
        )
        if not caminho:
            return
        try:
            registros = clienteApi.historico()
        except clienteApi.ErroApi as erro:
            QMessageBox.critical(self, "Erro", str(erro))
            return
        tarefa = ExportarHistorico(registros, caminho)
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

    # ------------------------------------------------------------------
    # Janela
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        resposta = QMessageBox.question(self, "Sair", "Deseja realmente sair da locadora?")
        if resposta == QMessageBox.Yes:
            self.timer.stop()
            for t in list(self.tarefas):
                t.wait()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete and self.tipo_usuario == "Admin":
            self.excluir_filme()

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