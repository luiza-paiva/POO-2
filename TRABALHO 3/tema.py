import json
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

from repositorio import PASTA_DADOS

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
}
CORES_ESCURO = {
    "fundo": "#2d2d2d", "campo": "#1e1e1e", "texto": "#e6e6e6",
    "suave": "#9aa0a6", "borda": "#5a5a5a", "destaque": "#2a82da",
    "hover": "rgba(255, 255, 255, 30)",
}

CAMINHO_CONFIG = PASTA_DADOS / "config.json"


_QSS_COMUM = """
QLabel#tituloFileira { font-size: 18px; font-weight: bold; }
QFrame#cartao QLabel { background: transparent; }
"""

_QSS_ESCURO = _QSS_COMUM + """
QFrame#cartao { background-color: #1f1f1f; border-radius: 10px; border: 10px solid #1f1f1f; }
QFrame#cartao:hover { background-color: #2a2a2a; border-color: #2a2a2a; }
QFrame#cartao[selecionado="true"] { border: 10px solid #e50914; }
"""

_QSS_CLARO = _QSS_COMUM + """
QFrame#cartao { background-color: #ffffff; border-radius: 10px; border: 10px solid #ffffff; }
QFrame#cartao:hover { background-color: #e9e9e9; border-color: #e9e9e9; }
QFrame#cartao[selecionado="true"] { border: 10px solid #e50914; }
"""

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
    fundo = QColor(220, 220, 220)
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
    app.setStyleSheet(_QSS_ESCURO if escuro else _QSS_CLARO)