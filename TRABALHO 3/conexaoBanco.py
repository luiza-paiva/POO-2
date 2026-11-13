from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USUARIO = "neo4j"
SENHA = "Jupiter07?"

driver = GraphDatabase.driver(URI, auth=(USUARIO, SENHA))

def consultar(query, **params):
    with driver.session() as sessao:
        return [r.data() for r in sessao.run(query, **params)]

def executar(query, **params):
    with driver.session() as sessao:
        sessao.run(query, **params)

def fechar():
    driver.close()

if __name__ == '__main__':
    print(consultar("MATCH (f:Filme) RETURN count(f) AS filmes"))
    fechar()