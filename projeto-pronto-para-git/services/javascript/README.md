# JavaScript Services

Implementacao Node.js do catalogo musical. A entrada publica permanece em `servers/*.js`, mas a implementacao real vive em `src/adapters/*/server.js` e usa `src/application/catalogService.js`.

Comandos:

```powershell
npm install --prefix services/javascript
npm --prefix services/javascript run check
npm --prefix services/javascript run rest
npm --prefix services/javascript run graphql
npm --prefix services/javascript run soap
npm --prefix services/javascript run grpc
```
