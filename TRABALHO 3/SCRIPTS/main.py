import sys

from PySide6.QtWidgets import QApplication

from janelaLogin import JanelaLogin
import tema

def main():
    app = QApplication(sys.argv)
    tema.aplicar_tema(tema.carregar_preferencia())

    janela_login = JanelaLogin()
    janela_login.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()