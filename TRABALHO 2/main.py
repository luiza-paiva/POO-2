import sys

from PySide6.QtWidgets import QApplication

from janelaLogin import JanelaLogin
from dialogos import JanelaAlugar, JanelaCadastro
from models import Filme, ALUGADO, DISPONIVEL
from historicoAlgueis import historico
from tarefas_arquivo import GravarDados

def main():
    app = QApplication(sys.argv)

    janela_login = JanelaLogin()
    janela_login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()