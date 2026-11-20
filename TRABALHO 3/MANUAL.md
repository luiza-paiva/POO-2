# Manual de execução - Locadora de Filmes

O sistema tem três partes, cada uma em um contêiner Docker: o PostgreSQL, o Neo4j e a API (FastAPI). O aplicativo PySide6 conversa só com a API.

## Antes de começar

- Docker Desktop instalado e aberto.
- Na pasta `TRABALHO 3`, criar um arquivo `.env` com as senhas (mínimo 8 caracteres):

```
POSTGRES_PASSWORD=sua_senha
NEO4J_PASSWORD=sua_senha
```

## Subir o sistema

Na pasta `TRABALHO 3`:

```
docker compose up -d --build
```

Para ver se subiu:

```
docker compose ps
```

O Neo4j demora uns 30 segundos para ficar pronto, e a API só inicia depois dele.

Depois é só abrir:

- http://localhost:8000/saude (mostra se os dois bancos estão ok)
- http://localhost:8000/docs (para testar as rotas)
- http://localhost:7474 (Neo4j Browser, usuário `neo4j`)

Na primeira vez a API cria sozinha o usuário `admin` (senha `admin`), os gêneros e os 15 filmes iniciais.

## Parar

```
docker compose stop        # para, mantendo os dados
docker compose down        # remove os contêineres, mantém os dados
docker compose down -v     # remove tudo, inclusive os dados
```

## Comandos úteis

Ver os logs da API:

```
docker compose logs -f api
```

Reconstruir só a API depois de mudar o código:

```
docker compose up -d --build api
```

Consultar o Postgres:

```
docker compose exec postgres psql -U locadora -d locadora -P pager=off -c "\dt"
docker compose exec postgres psql -U locadora -d locadora -P pager=off -c "SELECT * FROM usuarios"
```

Consultar o Neo4j (trocar SUA_SENHA pela senha do .env):

```
docker compose exec neo4j cypher-shell -u neo4j -p SUA_SENHA "MATCH (n) RETURN labels(n), count(n)"
```

## Se mudar o esquema.sql

O `esquema.sql` só é aplicado quando o banco está vazio. Para aplicar de novo:

```
docker compose down -v
docker compose up -d --build
```

## Problemas comuns

- `docker` não reconhecido: abrir o Docker Desktop e abrir um terminal novo.
- Porta em uso (8000, 7474): fechar o que está usando, por exemplo a API rodando no terminal.
- Mudei a senha no `.env` e não pegou: o banco guarda a senha antiga no volume. Usar `docker compose down -v` e subir de novo.
- Neo4j não fica pronto: esperar mais um pouco e ver `docker compose logs neo4j`.

## Rodar em outra máquina

Copiar a pasta do projeto, criar o `.env` e rodar `docker compose up -d --build`. No aplicativo, usar o endereço `http://IP-DA-MAQUINA:8000`.