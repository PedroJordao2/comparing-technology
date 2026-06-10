# Arquitetura

A refatoracao separa protocolo e regra de negocio. REST, GraphQL, SOAP e gRPC sao adapters independentes que chamam o mesmo servico de aplicacao. A massa sintetica e deterministica e reiniciada pela operacao `reset`.

## Comunicacao

- Cliente REST -> HTTP handler -> CatalogService.
- Cliente GraphQL -> schema/resolvers -> CatalogService.
- Cliente SOAP -> parser XML/WSDL -> CatalogService.
- Cliente gRPC -> contrato `music.streaming.v1` -> CatalogService.
