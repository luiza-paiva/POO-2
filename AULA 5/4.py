with open("exemplo.txt", "r", encoding="utf-8") as arquivo:
    linhas = arquivo.readlines()
    print(f"Total de linhas: {len(linhas)}")