import sys

from PySide6.QtWidgets import QApplication

from janela_login import JanelaLogin


def main():
    app = QApplication(sys.argv)

    janela_login = JanelaLogin()
    janela_login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()