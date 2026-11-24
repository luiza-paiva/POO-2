import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

from string import Template

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
    "superficie": "#ffffff", "superficie_hover": "#f7f7f7", "linha": "#e0e0e0",
    "destaque_hover": "#1f6fbf",
}
CORES_ESCURO = {
    "fundo": "#2d2d2d", "campo": "#1e1e1e", "texto": "#e6e6e6",
    "suave": "#9aa0a6", "borda": "#5a5a5a", "destaque": "#2a82da",
    "hover": "rgba(255, 255, 255, 30)",
    "superficie": "#363636", "superficie_hover": "#404040", "linha": "#454545",
    "destaque_hover": "#4a97e8",
}

PASTA_DADOS = Path(__file__).resolve().parent / "dados"
CAMINHO_CONFIG = PASTA_DADOS / "config.json"


ESTILO_APP = Template("""
QLabel#saudacao { font-size: 26px; font-weight: bold; }
QLabel#subtitulo { color: $suave; font-size: 13px; }
QLabel#vazio { color: $suave; font-size: 15px; }
QLabel#tituloFileira { font-size: 19px; font-weight: bold; }

QLineEdit#busca {
    background: $campo; color: $texto; border: 1px solid $borda;
    border-radius: 19px; padding: 9px 16px; font-size: 14px;
}
QLineEdit#busca:focus { border: 1px solid $destaque; }

QPushButton#chipGenero {
    background: transparent; color: $texto; border: 1px solid $borda;
    border-radius: 14px; padding: 6px 16px; font-size: 13px;
}
QPushButton#chipGenero:hover { background: $hover; }
QPushButton#chipGenero:checked {
    background: $destaque; border: 1px solid $destaque; color: #ffffff; font-weight: bold;
}

QPushButton#setaFileira {
    background: transparent; color: $texto; border: 1px solid $borda;
    border-radius: 15px; min-width: 30px; max-width: 30px;
    min-height: 30px; max-height: 30px; font-size: 18px; padding: 0 0 2px 0;
}
QPushButton#setaFileira:hover { background: $hover; }

QFrame#cartao {
    background: $superficie; border: 2px solid transparent; border-radius: 14px;
}
QFrame#cartao:hover { background: $superficie_hover; border: 2px solid $borda; }
QFrame#cartao[selecionado="true"] { border: 2px solid $destaque; }
QFrame#cartao QLabel { background: transparent; }
QLabel#cartaoTitulo { font-size: 14px; font-weight: bold; }
QLabel#cartaoNota { color: $suave; font-size: 12px; }

QScrollArea { background: transparent; border: none; }
QScrollBar:horizontal { height: 8px; background: transparent; margin: 0; }
QScrollBar::handle:horizontal { background: $borda; border-radius: 4px; min-width: 40px; }
QScrollBar:vertical { width: 10px; background: transparent; margin: 0; }
QScrollBar::handle:vertical { background: $borda; border-radius: 5px; min-height: 40px; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QScrollBar::add-page, QScrollBar::sub-page { background: transparent; }

QLabel#telaTitulo { font-size: 28px; font-weight: bold; }
QLabel#telaSecao { font-size: 16px; font-weight: bold; }
QLabel#telaTexto { font-size: 14px; }
QLabel#telaDica { color: $suave; font-size: 12px; }
QFrame#caixaAvaliacao {
    background: $superficie; border: 1px solid $linha; border-radius: 10px;
}
QFrame#caixaAvaliacao QLabel { background: transparent; }

QPushButton#botaoPrimario {
    background: $destaque; color: #ffffff; border: none; border-radius: 8px;
    padding: 11px 24px; font-weight: bold; font-size: 14px;
}
QPushButton#botaoPrimario:hover { background: $destaque_hover; }
QPushButton#botaoPrimario:disabled { background: $borda; color: $suave; }
QPushButton#botaoSecundario {
    background: transparent; color: $texto; border: 1px solid $borda;
    border-radius: 8px; padding: 10px 22px; font-size: 14px;
}
QPushButton#botaoSecundario:hover { background: $hover; }
QPushButton#botaoSecundario:disabled { color: $suave; border-color: $linha; }
QPushButton#botaoPerigo {
    background: transparent; color: #e5534b; border: 1px solid #e5534b;
    border-radius: 8px; padding: 10px 22px; font-size: 14px;
}
QPushButton#botaoPerigo:hover { background: rgba(229, 83, 75, 40); }
""")


def estilo_app(escuro: bool) -> str:
    return ESTILO_APP.substitute(CORES_ESCURO if escuro else CORES_CLARO)


def estilo_login() -> str:
    cores = CORES_ESCURO if carregar_preferencia() else CORES_CLARO
    return ESTILO.substitute(cores)

def carregar_preferencia(caminho: Path = CAMINHO_CONFIG) -> bool:
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            return json.load(f).get("tema") == "escuro"
    except (OSError, json.JSONDecodeError, AttributeError):
        return False


def salvar_preferencia(escuro: bool, caminho: Path = CAMINHO_CONFIG) -> None:
    try:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump({"tema": "escuro" if escuro else "claro"}, f, indent=2)
    except OSError:
        pass

def _paleta_escura() -> QPalette:
    p = QPalette()
    fundo = QColor(45, 45, 45)
    base = QColor(30, 30, 30)
    texto = QColor(230, 230, 230)
    destaque = QColor(42, 130, 218)
    desabilitado = QColor(127, 127, 127)

    p.setColor(QPalette.Window, fundo)
    p.setColor(QPalette.WindowText, texto)
    p.setColor(QPalette.Base, base)
    p.setColor(QPalette.AlternateBase, fundo)
    p.setColor(QPalette.ToolTipBase, base)
    p.setColor(QPalette.ToolTipText, texto)
    p.setColor(QPalette.Text, texto)
    p.setColor(QPalette.Button, fundo)
    p.setColor(QPalette.ButtonText, texto)
    p.setColor(QPalette.BrightText, QColor(255, 80, 80))
    p.setColor(QPalette.Link, destaque)
    p.setColor(QPalette.Highlight, destaque)
    p.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    p.setColor(QPalette.PlaceholderText, desabilitado)
    for papel in (QPalette.Text, QPalette.WindowText, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, papel, desabilitado)
    return p


def _paleta_clara() -> QPalette:
    p = QPalette()
    fundo = QColor(240, 240, 240)
    base = QColor(255, 255, 255)
    texto = QColor(26, 26, 26)
    destaque = QColor(42, 130, 218)
    desabilitado = QColor(140, 140, 140)

    p.setColor(QPalette.Window, fundo)
    p.setColor(QPalette.WindowText, texto)
    p.setColor(QPalette.Base, base)
    p.setColor(QPalette.AlternateBase, QColor(238, 238, 238))
    p.setColor(QPalette.ToolTipBase, base)
    p.setColor(QPalette.ToolTipText, texto)
    p.setColor(QPalette.Text, texto)
    p.setColor(QPalette.Button, QColor(233, 233, 233))
    p.setColor(QPalette.ButtonText, texto)
    p.setColor(QPalette.BrightText, QColor(200, 30, 30))
    p.setColor(QPalette.Link, destaque)
    p.setColor(QPalette.Highlight, destaque)
    p.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    p.setColor(QPalette.PlaceholderText, QColor(138, 138, 138))
    for papel in (QPalette.Text, QPalette.WindowText, QPalette.ButtonText):
        p.setColor(QPalette.Disabled, papel, desabilitado)
    return p


def alternar_tema() -> None:
    aplicar_tema(not carregar_preferencia())


def aplicar_tema(escuro: bool) -> None:
    app = QApplication.instance()
    app.setStyle("Fusion")
    estilo = app.styleHints()
    if hasattr(estilo, "setColorScheme"):
        estilo.setColorScheme(Qt.ColorScheme.Dark if escuro else Qt.ColorScheme.Light)
    app.setPalette(_paleta_escura() if escuro else _paleta_clara())
    salvar_preferencia(escuro)
    app.setStyleSheet(estilo_app(escuro))