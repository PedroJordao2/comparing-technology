# Music Catalog Distributed Services

Projeto distribuido com duas implementacoes equivalentes, em Python e JavaScript/Node.js, expondo o mesmo catalogo musical por REST, GraphQL, SOAP e gRPC. A refatoracao reorganiza o codigo por camadas e mantem os endpoints publicos usados nos scripts originais.

## Arquitetura

- **application**: regras de catalogo, validacao, mutacoes e consultas.
- **data**: geracao da massa sintetica inicial. A base inicia com 200 usuarios, 400 musicas e 300 playlists.
- **adapters**: pontos de entrada REST, GraphQL, SOAP e gRPC.
- **core/domain**: aliases de compatibilidade e erros de dominio.
- **proto**: contrato gRPC versionado em `music.streaming.v1`.

## Portas

| Stack | REST | GraphQL | SOAP | gRPC |
| --- | ---: | ---: | ---: | ---: |
| Python | 3000 | 3001 | 3002 | 50051 |
| JavaScript | 3100 | 3101 | 3102 | 55051 |

## Executando com Docker Compose

```powershell
docker compose build
docker compose up rest-python graphql-python soap-python grpc-python rest-js graphql-js soap-js grpc-js
```

## REST

```powershell
Invoke-RestMethod http://localhost:3000/health
Invoke-RestMethod http://localhost:3000/users
Invoke-RestMethod -Method Post http://localhost:3000/users -ContentType 'application/json' -Body '{"name":"Novo Ouvinte","email":"novo@example.test"}'
```

## GraphQL

```powershell
Invoke-RestMethod -Method Post http://localhost:3001/graphql -ContentType 'application/json' -Body '{"query":"query { users { id name email } }"}'
```

## SOAP

```powershell
$body = '<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><ListSongs xmlns="http://example.com/music-streaming"/></soap:Body></soap:Envelope>'
Invoke-RestMethod -Method Post http://localhost:3002/soap -ContentType 'text/xml' -Body $body
```

## gRPC

O contrato fica em `proto/music.proto`. Exemplo com grpcurl:

```powershell
grpcurl -plaintext localhost:50051 music.streaming.v1.MusicCatalogService/ListUsers
```

## Fluxos

1. O adapter recebe a requisicao do protocolo.
2. O payload e normalizado para o formato da aplicacao.
3. `CatalogService` executa validacoes, consultas e mutacoes em memoria.
4. O adapter serializa a resposta no protocolo correspondente.

## Validacao Recomendada

```powershell
npm --prefix services/javascript run check
py -m compileall services/python/music_service
docker compose config
docker compose build
```
