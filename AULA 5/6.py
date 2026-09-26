with open("entrada.txt", "r", encoding="utf-8") as origem:
    conteudo = origem.read()

with open("copia.txt", "w", encoding="utf-8") as destino:
    destino.write(conteudo)