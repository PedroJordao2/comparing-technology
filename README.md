Segue um `README.md` pronto para colocar no Git:

```md
# Music Catalog Distributed Services

Projeto de serviços distribuídos para um catálogo musical, implementado em **Python** e **JavaScript/Node.js**, expondo as mesmas funcionalidades por diferentes protocolos:

- REST
- GraphQL
- SOAP
- gRPC

O projeto também possui suporte a Docker, Docker Compose e scripts de execução/carga com Locust.

## Tecnologias

- Python
- JavaScript / Node.js
- REST
- GraphQL
- SOAP
- gRPC
- Docker
- Docker Compose
- Locust

## Estrutura do Projeto

```text
.
├── proto/
│   └── music.proto
├── services/
│   ├── python/
│   │   ├── music_service/
│   │   │   ├── adapters/
│   │   │   ├── application/
│   │   │   ├── core/
│   │   │   ├── data/
│   │   │   ├── domain/
│   │   │   ├── generated/
│   │   │   └── servers/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── javascript/
│       ├── src/
│       │   ├── adapters/
│       │   ├── application/
│       │   ├── core/
│       │   └── data/
│       ├── servers/
│       ├── Dockerfile
│       └── package.json
├── scripts/
├── docs/
├── docker-compose.yml
├── locustfile.py
└── README.md
```

## Massa de Dados

A aplicação inicia com dados sintéticos em memória:

- 200 usuários
- 400 músicas
- 300 playlists

Os dados podem ser reiniciados usando o endpoint `/reset`.

## Portas dos Serviços

| Stack | REST | GraphQL | SOAP | gRPC |
|---|---:|---:|---:|---:|
| Python | 3000 | 3001 | 3002 | 50051 |
| JavaScript | 3100 | 3101 | 3102 | 55051 |

## Executando com Docker

### 1. Build das imagens

```powershell
docker compose build
```

### 2. Subir todos os serviços

```powershell
docker compose up
```

Ou em segundo plano:

```powershell
docker compose up -d
```

### 3. Verificar containers

```powershell
docker compose ps
```

### 4. Parar os serviços

```powershell
docker compose down
```

## Executando sem Docker

### Instalar dependências Python

```powershell
py -m pip install -r services/python/requirements.txt
```

### Instalar dependências JavaScript

```powershell
npm ci --prefix services/javascript
```

### Rodar serviços Python

REST:

```powershell
$env:PYTHONPATH="services/python"; py -m music_service.adapters.rest.server
```

GraphQL:

```powershell
$env:PYTHONPATH="services/python"; py -m music_service.adapters.graphql.server
```

SOAP:

```powershell
$env:PYTHONPATH="services/python"; py -m music_service.adapters.soap.server
```

gRPC:

```powershell
$env:PYTHONPATH="services/python"; py -m music_service.adapters.grpc.server
```

### Rodar serviços JavaScript

REST:

```powershell
npm --prefix services/javascript run rest
```

GraphQL:

```powershell
npm --prefix services/javascript run graphql
```

SOAP:

```powershell
npm --prefix services/javascript run soap
```

gRPC:

```powershell
npm --prefix services/javascript run grpc
```

## Scripts Prontos

Subir todos os serviços Python com Docker:

```powershell
.\scripts\start_services\python_all.ps1
```

Subir todos os serviços JavaScript com Docker:

```powershell
.\scripts\start_services\javascript_all.ps1
```

Rodar bateria completa de testes/carga:

```powershell
.\scripts\run_all.ps1
```

Rodar somente Python:

```powershell
.\scripts\run_python.ps1
```

Rodar somente JavaScript:

```powershell
.\scripts\run_javascript.ps1
```

## Exemplos de Uso

### REST

Healthcheck Python:

```powershell
Invoke-RestMethod http://localhost:3000/health
```

Listar usuários Python:

```powershell
Invoke-RestMethod http://localhost:3000/users
```

Criar usuário Python:

```powershell
Invoke-RestMethod -Method Post http://localhost:3000/users `
  -ContentType "application/json" `
  -Body '{"name":"Pedro Teste","email":"pedro.teste@example.com"}'
```

Listar usuários JavaScript:

```powershell
Invoke-RestMethod http://localhost:3100/users
```

### GraphQL

Python:

```powershell
Invoke-RestMethod -Method Post http://localhost:3001/graphql `
  -ContentType "application/json" `
  -Body '{"query":"query { users { id name email } }"}'
```

JavaScript:

```powershell
Invoke-RestMethod -Method Post http://localhost:3101/graphql `
  -ContentType "application/json" `
  -Body '{"query":"query { songs { id title artist album durationSeconds } }"}'
```

### SOAP

Python:

```powershell
$body = '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><ListUsers xmlns="http://example.com/music-streaming"/></soap:Body></soap:Envelope>'

Invoke-RestMethod -Method Post http://localhost:3002/soap `
  -ContentType "text/xml" `
  -Body $body
```

JavaScript:

```powershell
$body = '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><ListSongs xmlns="http://example.com/music-streaming"/></soap:Body></soap:Envelope>'

Invoke-RestMethod -Method Post http://localhost:3102/soap `
  -ContentType "text/xml" `
  -Body $body
```

### gRPC

O contrato gRPC está em:

```text
proto/music.proto
```

Exemplo usando `grpcurl`:

```powershell
grpcurl -plaintext localhost:50051 list
```

```powershell
grpcurl -plaintext localhost:50051 music.streaming.v1.MusicCatalogService/ListUsers
```

JavaScript:

```powershell
grpcurl -plaintext localhost:55051 music.streaming.v1.MusicCatalogService/ListSongs
```

## Validação

### Python

```powershell
py -m compileall services/python/music_service
```

### JavaScript

```powershell
npm --prefix services/javascript run check
```

### Docker Compose

```powershell
docker compose config
```

## Testes de Carga

O projeto usa Locust para cenários de carga.

Arquivo principal:

```text
locustfile.py
```

Rodar todos os cenários:

```powershell
.\scripts\run_all.ps1
```

Os resultados são gerados em:

```text
results/
```

A pasta `results/` não é versionada no Git porque contém arquivos gerados.

## Observações sobre Git

Arquivos e pastas ignorados:

```text
node_modules/
results/
*.zip
__pycache__/
*.pyc
.venv/
.pytest_cache/
```

Depois de clonar o projeto, reinstale as dependências:

```powershell
npm ci --prefix services/javascript
py -m pip install -r services/python/requirements.txt
```

Ou use Docker:

```powershell
docker compose build
docker compose up
```

## Autor
Pedro Enrique Jordao 
Amanda Evelin
Rogerio Bruno
Projeto acadêmico de Computação Distribuída.
```
