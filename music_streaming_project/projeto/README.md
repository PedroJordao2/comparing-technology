# Music Streaming Service — Comparação SOAP · REST · GraphQL · gRPC

Projeto da disciplina **Computação Distribuída** — Prof. Nabor C. Mendonça  
Implementação do serviço de streaming de músicas nas quatro tecnologias em **Python**.

---

## Estrutura do Projeto

```
projeto/
├── shared/
│   └── database.py          # banco em memória compartilhado + seed
├── rest/
│   └── server.py            # FastAPI — porta 8001
├── graphql_service/
│   └── server.py            # Strawberry + FastAPI — porta 8002
├── grpc_service/
│   ├── music.proto          # definição do protocolo
│   ├── server.py            # servidor gRPC — porta 50051
│   └── music_pb2*.py        # stubs gerados (ver abaixo)
├── soap/
│   └── server.py            # Spyne — porta 8003
├── tests/
│   ├── load_test.py         # cenários Locust
│   └── generate_graphs.py   # geração de gráficos matplotlib
├── requirements.txt
└── README.md
```

---

## Instalação

```bash
# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Instale as dependências
pip install -r requirements.txt
```

---

## Rodando os Servidores

### 1. REST (FastAPI) — porta 8001
```bash
python rest/server.py
# Docs: http://localhost:8001/docs
```

### 2. GraphQL (Strawberry) — porta 8002
```bash
python graphql_service/server.py
# Playground: http://localhost:8002/graphql
```

### 3. gRPC — porta 50051

Primeiro, gere os stubs Python a partir do `.proto`:
```bash
cd grpc_service
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. music.proto
cd ..
```

Depois, inicie o servidor:
```bash
python grpc_service/server.py
```

### 4. SOAP (Spyne) — porta 8003
```bash
python soap/server.py
# WSDL: http://localhost:8003/?wsdl
```

---

## Exemplos de Uso

### REST
```bash
# Listar usuários
curl http://localhost:8001/users

# Criar usuário
curl -X POST http://localhost:8001/users \
  -H "Content-Type: application/json" \
  -d '{"nome": "Ana", "idade": 28}'

# Listar músicas de uma playlist
curl http://localhost:8001/playlists/1/songs
```

### GraphQL
```graphql
# No Playground em http://localhost:8002/graphql

# Listar usuários
{ users { id nome idade } }

# Criar música
mutation {
  createSong(input: { nome: "Imagine", artista: "John Lennon" }) { id }
}

# Playlists de um usuário
{ userPlaylists(usuarioId: 1) { id nome musicas } }
```

### gRPC (com grpcurl)
```bash
# Instale grpcurl: https://github.com/fullstorydev/grpcurl
grpcurl -plaintext -proto grpc_service/music.proto \
  -d '{}' localhost:50051 music.UserService/ListUsers
```

### SOAP (com curl)
```bash
curl -X POST http://localhost:8003/ \
  -H "Content-Type: text/xml" \
  -H "SOAPAction: list_users" \
  -d '<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="music.streaming">
  <soap:Body><tns:list_users/></soap:Body>
</soap:Envelope>'
```

---

## Testes de Carga

### Pré-requisito: todos os servidores em execução

### Rodar o Locust (interface web)
```bash
# Escolha a tecnologia pelo nome da classe:
# RestUser | GraphQLUser | SOAPUser

locust -f tests/load_test.py RestUser
# Acesse: http://localhost:8089
# Configure: usuários simultâneos e taxa de spawn
```

### Rodar sem interface (modo headless)
```bash
locust -f tests/load_test.py RestUser \
  --headless -u 100 -r 10 --run-time 60s \
  --csv tests/results/rest

locust -f tests/load_test.py GraphQLUser \
  --headless -u 100 -r 10 --run-time 60s \
  --csv tests/results/graphql

locust -f tests/load_test.py SOAPUser \
  --headless -u 100 -r 10 --run-time 60s \
  --csv tests/results/soap
```

### Gerar Gráficos
```bash
# Com dados reais do Locust (CSVs em tests/results/)
python tests/generate_graphs.py

# Gráficos salvos em tests/graphs/
```

---

## Cargas Testadas

| Usuários | Descrição          |
|----------|--------------------|
| 10       | Carga baixa        |
| 50       | Carga moderada     |
| 100      | Carga alta         |
| 500      | Carga muito alta   |

## Métricas Coletadas

- Tempo médio de resposta (ms)
- Requisições por segundo (RPS)
- Taxa de erros (%)
- Tempo mínimo e máximo de resposta

---

## Modelo de Dados

```
Usuário (id, nome, idade)
    └── 0..* Playlists
                └── 1..* Músicas ←── Música (id, nome, artista)
```

## Operações Disponíveis (todas as tecnologias)

| Recurso   | Criar | Listar | Buscar | Atualizar | Deletar | Extra |
|-----------|-------|--------|--------|-----------|---------|-------|
| Usuário   | ✔     | ✔      | ✔      | ✔         | ✔       | Listar playlists do usuário |
| Música    | ✔     | ✔      | ✔      | ✔         | ✔       | Listar playlists da música |
| Playlist  | ✔     | ✔      | ✔      | ✔         | ✔       | Adicionar/remover músicas, listar músicas |
