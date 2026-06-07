# =============================================================
# Testes de Carga — Locust
# Uso:
#   locust -f load_test.py --host http://localhost:8001 RestUser
#   locust -f load_test.py --host http://localhost:8002 GraphQLUser
#   locust -f load_test.py --host http://localhost:8003 SOAPUser
# Ou acesse http://localhost:8089 para a interface web do Locust
# =============================================================

import json
import random
from locust import HttpUser, task, between, tag


# ══════════════════════════════════════════════════════════════
# REST
# ══════════════════════════════════════════════════════════════

class RestUser(HttpUser):
    """Simula um cliente do serviço REST (porta 8001)."""
    host = "http://localhost:8001"
    wait_time = between(0.1, 0.5)

    def on_start(self):
        """Cria dados iniciais para os testes."""
        r = self.client.post("/users", json={"nome": "Teste", "idade": 20})
        self.user_id = r.json().get("id", 1)

        r = self.client.post("/songs", json={"nome": "Song Test", "artista": "Artist"})
        self.song_id = r.json().get("id", 1)

        r = self.client.post("/playlists", json={
            "nome": "PL Test", "usuario_id": self.user_id,
            "musicas": [self.song_id]
        })
        self.playlist_id = r.json().get("id", 1)

    @task(3)
    @tag("list")
    def list_users(self):
        self.client.get("/users", name="REST: Listar Usuários")

    @task(3)
    @tag("list")
    def list_songs(self):
        self.client.get("/songs", name="REST: Listar Músicas")

    @task(2)
    @tag("list")
    def list_playlist_songs(self):
        self.client.get(f"/playlists/{self.playlist_id}/songs",
                        name="REST: Músicas da Playlist")

    @task(2)
    @tag("list")
    def list_user_playlists(self):
        self.client.get(f"/users/{self.user_id}/playlists",
                        name="REST: Playlists do Usuário")

    @task(1)
    @tag("create")
    def create_user(self):
        self.client.post("/users",
                         json={"nome": f"User{random.randint(1,9999)}", "idade": 22},
                         name="REST: Criar Usuário")

    @task(1)
    @tag("create")
    def create_song(self):
        self.client.post("/songs",
                         json={"nome": f"Song{random.randint(1,9999)}", "artista": "Band"},
                         name="REST: Criar Música")


# ══════════════════════════════════════════════════════════════
# GraphQL
# ══════════════════════════════════════════════════════════════

class GraphQLUser(HttpUser):
    """Simula um cliente do serviço GraphQL (porta 8002)."""
    host = "http://localhost:8002"
    wait_time = between(0.1, 0.5)

    def gql(self, query: str, variables: dict = None, name: str = "GraphQL"):
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        return self.client.post("/graphql",
                                json=payload,
                                headers={"Content-Type": "application/json"},
                                name=name)

    def on_start(self):
        r = self.gql("""
            mutation { createUser(input: {nome: "GQL Test", idade: 25}) { id } }
        """, name="GQL: Setup User")
        self.user_id = r.json()["data"]["createUser"]["id"]

        r = self.gql("""
            mutation { createSong(input: {nome: "GQL Song", artista: "GQL Band"}) { id } }
        """, name="GQL: Setup Song")
        self.song_id = r.json()["data"]["createSong"]["id"]

        r = self.gql(f"""
            mutation {{
              createPlaylist(input: {{nome: "GQL PL", usuario_id: {self.user_id},
                musicas: [{self.song_id}]}}) {{ id }}
            }}
        """, name="GQL: Setup Playlist")
        self.playlist_id = r.json()["data"]["createPlaylist"]["id"]

    @task(3)
    def list_users(self):
        self.gql("{ users { id nome idade } }", name="GQL: Listar Usuários")

    @task(3)
    def list_songs(self):
        self.gql("{ songs { id nome artista } }", name="GQL: Listar Músicas")

    @task(2)
    def playlist_songs(self):
        self.gql(f"{{ playlistSongs(playlistId: {self.playlist_id}) {{ id nome }} }}",
                 name="GQL: Músicas da Playlist")

    @task(2)
    def user_playlists(self):
        self.gql(f"{{ userPlaylists(usuarioId: {self.user_id}) {{ id nome }} }}",
                 name="GQL: Playlists do Usuário")

    @task(1)
    def create_user(self):
        n = random.randint(1, 9999)
        self.gql(f'mutation {{ createUser(input: {{nome: "U{n}", idade: 20}}) {{ id }} }}',
                 name="GQL: Criar Usuário")

    @task(1)
    def create_song(self):
        n = random.randint(1, 9999)
        self.gql(f'mutation {{ createSong(input: {{nome: "S{n}", artista: "A"}}) {{ id }} }}',
                 name="GQL: Criar Música")


# ══════════════════════════════════════════════════════════════
# SOAP
# ══════════════════════════════════════════════════════════════

SOAP_ENVELOPE = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:tns="music.streaming">
  <soap:Body>
    {body}
  </soap:Body>
</soap:Envelope>"""

class SOAPUser(HttpUser):
    """Simula um cliente do serviço SOAP (porta 8003)."""
    host = "http://localhost:8003"
    wait_time = between(0.1, 0.5)

    def soap(self, body: str, action: str, name: str = "SOAP"):
        envelope = SOAP_ENVELOPE.format(body=body)
        return self.client.post("/",
            data=envelope.encode("utf-8"),
            headers={
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": action,
            },
            name=name)

    def on_start(self):
        self.user_id = 1
        self.song_id = 1
        self.playlist_id = 1

    @task(3)
    def list_users(self):
        self.soap("<tns:list_users/>", "list_users", "SOAP: Listar Usuários")

    @task(3)
    def list_songs(self):
        self.soap("<tns:list_songs/>", "list_songs", "SOAP: Listar Músicas")

    @task(2)
    def playlist_songs(self):
        self.soap(
            f"<tns:get_playlist_songs><tns:id>{self.playlist_id}</tns:id></tns:get_playlist_songs>",
            "get_playlist_songs", "SOAP: Músicas da Playlist")

    @task(2)
    def user_playlists(self):
        self.soap(
            f"<tns:get_user_playlists><tns:usuario_id>{self.user_id}</tns:usuario_id></tns:get_user_playlists>",
            "get_user_playlists", "SOAP: Playlists do Usuário")

    @task(1)
    def create_user(self):
        n = random.randint(1, 9999)
        self.soap(
            f"<tns:create_user><tns:nome>U{n}</tns:nome><tns:idade>20</tns:idade></tns:create_user>",
            "create_user", "SOAP: Criar Usuário")

    @task(1)
    def create_song(self):
        n = random.randint(1, 9999)
        self.soap(
            f"<tns:create_song><tns:nome>S{n}</tns:nome><tns:artista>Band</tns:artista></tns:create_song>",
            "create_song", "SOAP: Criar Música")
