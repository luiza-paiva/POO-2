import json
from pathlib import Path

from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication

from repositorio import PASTA_DADOS

CAMINHO_CONFIG = PASTA_DADOS / "config.json"


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


def aplicar_tema(escuro: bool) -> None:
    app = QApplication.instance()
    app.setStyle("Fusion")
    app.setPalette(_paleta_escura() if escuro else app.style().standardPalette())
    salvar_preferencia(escuro)
