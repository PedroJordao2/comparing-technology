# Python Services

Implementacao Python do catalogo musical. Os modulos antigos em `music_service.servers` foram preservados como wrappers; os adapters reais ficam em `music_service.adapters`.

Comandos:

```powershell
py -m pip install -r services/python/requirements.txt
py -m compileall services/python/music_service
py -m music_service.adapters.rest.server
py -m music_service.adapters.graphql.server
py -m music_service.adapters.soap.server
py -m music_service.adapters.grpc.server
```
