with open("exemplo.txt", "r", encoding="utf-8") as arquivo:
    conteudo = arquivo.read()

conteudo_modificado = conteudo.replace("Python", "Java")

with open("saida_java.txt", "w", encoding="utf-8") as arquivo:
    arquivo.write(conteudo_modificado)