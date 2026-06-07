# Music Streaming Service

**Disciplina:** Computação Distribuída — Prof. Nabor C. Mendonça  
Comparação entre REST, GraphQL, gRPC e SOAP em Python.

---

## Estrutura de Pastas

```
projeto/
├── shared/database.py        # banco em memória + dados iniciais
├── rest/server.py            # REST (FastAPI) — porta 8001
├── graphql_service/server.py # GraphQL (Strawberry) — porta 8002
├── grpc_service/
│   ├── music.proto           # definição do protocolo
│   └── server.py             # gRPC — porta 50051
├── soap/server.py            # SOAP (Spyne) — porta 8003
├── tests/
│   ├── load_test.py          # testes de carga (Locust)
│   └── generate_graphs.py    # geração de gráficos
└── requirements.txt
```

---

## Como Rodar

### 1. Instalar dependências

```bash
py -m pip install fastapi "uvicorn[standard]" pydantic "strawberry-graphql[fastapi]" grpcio grpcio-tools lxml locust matplotlib numpy git+https://github.com/arskom/spyne.git
```

### 2. Gerar stubs do gRPC (só na primeira vez)

```bash
cd grpc_service
py -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. music.proto
cd ..
```

### 3. Rodar os servidores (um terminal para cada)

```bash
py rest/server.py
py graphql_service/server.py
py soap/server.py
py grpc_service/server.py
```

### 4. Acessar no navegador

| Tecnologia | Link                          |
| ---------- | ----------------------------- |
| REST       | http://localhost:8001/docs    |
| GraphQL    | http://localhost:8002/graphql |
| SOAP       | http://localhost:8003/?wsdl   |
| gRPC       | porta 50051                   |

---

## Testes de Carga

Com todos os servidores rodando, abra um novo terminal e execute:

```bash
py -m locust -f tests/load_test.py RestUser --headless -u 10 -r 2 --run-time 30s --csv tests/results/rest
py -m locust -f tests/load_test.py GraphQLUser --headless -u 10 -r 2 --run-time 30s --csv tests/results/graphql
py -m locust -f tests/load_test.py SOAPUser --headless -u 10 -r 2 --run-time 30s --csv tests/results/soap
```

### Gerar gráficos

```bash
py tests/generate_graphs.py
# Gráficos salvos em tests/graphs/
```

---

## Cargas Testadas

| Usuários | Descrição        |
| -------- | ---------------- |
| 10       | Carga baixa      |
| 50       | Carga moderada   |
| 100      | Carga alta       |
| 500      | Carga muito alta |

## Métricas Coletadas

- Tempo médio de resposta (ms)
- Requisições por segundo (RPS)
- Taxa de erros (%)
- Tempo mínimo e máximo de resposta

---

## Modelo de Dados

```
Usuário (id, nome, idade)
    └── Playlists
            └── Músicas (id, nome, artista)
```

## Operações Disponíveis

| Recurso  | Criar | Listar | Buscar | Atualizar | Deletar | Extra                       |
| -------- | ----- | ------ | ------ | --------- | ------- | --------------------------- |
| Usuário  | ✔     | ✔      | ✔      | ✔         | ✔       | Listar playlists do usuário |
| Música   | ✔     | ✔      | ✔      | ✔         | ✔       | Listar playlists da música  |
| Playlist | ✔     | ✔      | ✔      | ✔         | ✔       | Adicionar/remover músicas   |
