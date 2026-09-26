vogais = "aeiouAEIOU"

with open("exemplo.txt", "r", encoding="utf-8") as arquivo:
    conteudo = arquivo.read()

vogais_encontradas = [letra for letra in conteudo if letra in vogais]

with open("vogais.txt", "w", encoding="utf-8") as arquivo:
    arquivo.write("".join(vogais_encontradas))