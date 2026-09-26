with open("exemplo.txt", "r", encoding="utf-8") as arquivo:
    linhas = arquivo.readlines()

linha_mais_longa = max(linhas, key=len)
print(linha_mais_longa)