from html import escape

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea,
    QWidget, QFrame
)

import clienteApi
from models import Avaliacao
from cartaoFilme import gerar_poster, CORES_GENERO, COR_ESTRELA

LARGURA_POSTER = 250
ALTURA_POSTER = 370


def _estilo_etiqueta(cor):
    return (f"background: {cor}; color: white; font-size: 12px; font-weight: bold;"
            "border-radius: 10px; padding: 4px 12px;")


class TelaFilme(QDialog):
    def __init__(self, janela, filme):
        super().__init__(janela)
        self.janela = janela
        self.filme = filme
        self.ehAdmin = janela.tipo_usuario == "Admin"

        self.setWindowTitle(filme.titulo)
        self.resize(860, 560)
        self.setMinimumSize(720, 500)

        self.poster = QLabel()
        self.poster.setFixedSize(LARGURA_POSTER, ALTURA_POSTER)
        colunaPoster = QVBoxLayout()
        colunaPoster.addWidget(self.poster)
        colunaPoster.addStretch()

        self.titulo = QLabel()
        self.titulo.setObjectName("telaTitulo")
        self.titulo.setWordWrap(True)

        self.etGenero = QLabel()
        self.etStatus = QLabel()
        etiquetas = QHBoxLayout()
        etiquetas.setSpacing(8)
        etiquetas.addWidget(self.etGenero)
        etiquetas.addWidget(self.etStatus)
        etiquetas.addStretch()

        self.notaGrande = QLabel()
        self.notaQtd = QLabel()
        self.notaQtd.setObjectName("subtitulo")
        linhaNota = QHBoxLayout()
        linhaNota.setSpacing(10)
        linhaNota.addWidget(self.notaGrande)
        linhaNota.addWidget(self.notaQtd)
        linhaNota.addStretch()

        secaoSinopse = QLabel("Sinopse")
        secaoSinopse.setObjectName("telaSecao")
        self.sinopse = QLabel()
        self.sinopse.setObjectName("telaTexto")
        self.sinopse.setWordWrap(True)
        self.sinopse.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.sinopse.setTextFormat(Qt.RichText)

        self.secaoAvaliacoes = QLabel("O que acharam")
        self.secaoAvaliacoes.setObjectName("telaSecao")
        self.listaAvaliacoes = QVBoxLayout()
        self.listaAvaliacoes.setSpacing(8)

        miolo = QWidget()
        miolo.setAutoFillBackground(False)
        colunaMiolo = QVBoxLayout(miolo)
        colunaMiolo.setContentsMargins(0, 0, 10, 0)
        colunaMiolo.setSpacing(8)
        colunaMiolo.addWidget(secaoSinopse)
        colunaMiolo.addWidget(self.sinopse)
        colunaMiolo.addSpacing(10)
        colunaMiolo.addWidget(self.secaoAvaliacoes)
        colunaMiolo.addLayout(self.listaAvaliacoes)
        colunaMiolo.addStretch()

        rolagem = QScrollArea()
        rolagem.setWidgetResizable(True)
        rolagem.setFrameShape(QFrame.NoFrame)
        rolagem.setWidget(miolo)
        rolagem.viewport().setAutoFillBackground(False)

        self.dica = QLabel()
        self.dica.setObjectName("telaDica")
        self.dica.setWordWrap(True)

        botoes = QHBoxLayout()
        botoes.setSpacing(10)
        if self.ehAdmin:
            self.botaoEditar = self._botao("Editar filme", "botaoPrimario", self._editar)
            self.botaoExcluir = self._botao("Excluir", "botaoPerigo", self._excluir)
            botoes.addWidget(self.botaoEditar)
            botoes.addWidget(self.botaoExcluir)
        else:
            self.botaoAlugar = self._botao("Alugar filme", "botaoPrimario", self._alugar_ou_devolver)
            self.botaoAvaliar = self._botao("★  Avaliar filme", "botaoSecundario", self._avaliar)
            botoes.addWidget(self.botaoAlugar)
            botoes.addWidget(self.botaoAvaliar)
        botoes.addStretch()
        self.botaoFechar = self._botao("Fechar", "botaoSecundario", self.accept)
        self.botaoFechar.setAutoDefault(False)
        botoes.addWidget(self.botaoFechar)

        colunaInfo = QVBoxLayout()
        colunaInfo.setSpacing(10)
        colunaInfo.addWidget(self.titulo)
        colunaInfo.addLayout(etiquetas)
        colunaInfo.addLayout(linhaNota)
        colunaInfo.addSpacing(6)
        colunaInfo.addWidget(rolagem, 1)
        colunaInfo.addWidget(self.dica)
        colunaInfo.addLayout(botoes)

        raiz = QHBoxLayout(self)
        raiz.setContentsMargins(28, 28, 28, 24)
        raiz.setSpacing(30)
        raiz.addLayout(colunaPoster)
        raiz.addLayout(colunaInfo, 1)

        self.atualizar()

    def _botao(self, texto, nome, funcao):
        botao = QPushButton(texto)
        botao.setObjectName(nome)
        botao.setCursor(Qt.PointingHandCursor)
        botao.clicked.connect(funcao)
        return botao

    def _buscar_avaliacoes(self, filme_id):
        try:
            dados = clienteApi.listar_avaliacoes(filme_id)
        except clienteApi.ErroApi:
            return []
        return [Avaliacao(filme_id, d["usuario"], d["nota"],
                          d.get("comentario", ""), d.get("data_hora", ""))
                for d in dados]

    def atualizar(self):
        j = self.janela
        # A janela principal troca os objetos Filme a cada recarga da API.
        if j.filmeAtual is not None:
            self.filme = j.filmeAtual
        f = self.filme

        self.setWindowTitle(f.titulo)
        self.titulo.setText(f.titulo)
        self.poster.setPixmap(gerar_poster(f, LARGURA_POSTER, ALTURA_POSTER, 14))

        self.etGenero.setText(f.genero.capitalize())
        self.etGenero.setStyleSheet(_estilo_etiqueta(CORES_GENERO.get(f.genero, "#555555")))

        if f.disponivel:
            self.etStatus.setText(f"Disponível: {f.copias_disponiveis} de {f.copias}")
            self.etStatus.setStyleSheet(_estilo_etiqueta("#1e8c50"))
        else:
            self.etStatus.setText("Indisponível")
            self.etStatus.setStyleSheet(_estilo_etiqueta("#b9372d"))

        avaliacoes = self._buscar_avaliacoes(f.id)
        if avaliacoes:
            media = sum(a.nota for a in avaliacoes) / len(avaliacoes)
            self.notaGrande.setText(
                f"<span style='font-size:22px; color:{COR_ESTRELA}'>★</span> "
                f"<span style='font-size:22px; font-weight:bold'>{media:.1f}</span>".replace(".", ","))
            self.notaQtd.setText(f"{len(avaliacoes)} avaliaç{'ão' if len(avaliacoes) == 1 else 'ões'}")
        else:
            self.notaGrande.setText("")
            self.notaQtd.setText("Ainda sem avaliações")
        self.notaGrande.setVisible(bool(avaliacoes))

        if f.sinopse.strip():
            texto = escape(f.sinopse.strip()).replace("\n", "<br>")
        elif self.ehAdmin:
            texto = "<i>Sem sinopse. Use “Editar filme” para adicionar uma.</i>"
        else:
            texto = "<i>Este filme ainda não tem sinopse.</i>"
        self.sinopse.setText(f"<p style='line-height:150%'>{texto}</p>")

        self._preencher_avaliacoes(avaliacoes)
        if self.ehAdmin:
            self.dica.setText("")
        else:
            self._atualizar_botoes_usuario(avaliacoes)

    def _preencher_avaliacoes(self, avaliacoes):
        while self.listaAvaliacoes.count():
            item = self.listaAvaliacoes.takeAt(0)
            w = item.widget()
            if w is not None:
                w.hide()
                w.setParent(None)
                w.deleteLater()

        self.secaoAvaliacoes.setVisible(bool(avaliacoes))
        # A API já devolve da avaliação mais recente para a mais antiga.
        for a in avaliacoes:
            nome = "Você" if a.usuario == self.janela.login else escape(a.usuario)
            estrelas = (f"<span style='color:{COR_ESTRELA}'>{'★' * a.nota}</span>"
                        f"<span style='color:#8a8a8a'>{'★' * (5 - a.nota)}</span>")
            html = f"<b>{nome}</b>&nbsp;&nbsp;{estrelas}"
            if a.comentario.strip():
                html += f"<br>{escape(a.comentario.strip())}"
            caixa = QFrame()
            caixa.setObjectName("caixaAvaliacao")
            interno = QVBoxLayout(caixa)
            interno.setContentsMargins(14, 10, 14, 10)
            rotulo = QLabel(html)
            rotulo.setWordWrap(True)
            interno.addWidget(rotulo)
            self.listaAvaliacoes.addWidget(caixa)

    def _atualizar_botoes_usuario(self, avaliacoes):
        f, j = self.filme, self.janela

        if f.alugado_por == j.login:
            self.botaoAlugar.setText("Devolver filme")
            self.botaoAlugar.setEnabled(True)
        elif f.disponivel:
            self.botaoAlugar.setText("Alugar filme")
            self.botaoAlugar.setEnabled(True)
        else:
            self.botaoAlugar.setText("Indisponível")
            self.botaoAlugar.setEnabled(False)

        minha = next((a for a in avaliacoes if a.usuario == j.login), None)
        alugou = j.ja_alugou(f)
        self.botaoAvaliar.setEnabled(alugou)
        self.botaoAvaliar.setText("★  Editar minha avaliação" if minha else "★  Avaliar filme")
        self.dica.setText("" if alugou else "Alugue este filme para poder avaliá-lo.")

    def _alugar_ou_devolver(self):
        if self.filme.alugado_por == self.janela.login:
            self.janela.devolver_filme()
        else:
            self.janela.abrir_alugar()
        self.atualizar()

    def _avaliar(self):
        self.janela.avaliar_filme()
        self.atualizar()

    def _editar(self):
        self.janela.editar_filme()
        self.atualizar()

    def _excluir(self):
        self.janela.excluir_filme()
        if self.janela.filmeAtual is None:
            self.accept()
        else:
            self.atualizar()