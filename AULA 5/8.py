import os

if os.path.exists("exemplo.txt"):
    with open("exemplo.txt", "r", encoding="utf-8") as arquivo:
        conteudo = arquivo.read()
        print(conteudo)
else:
    print("O arquivo 'exemplo.txt' não existe.")