# =============================================================
# Servidor GraphQL — Strawberry + FastAPI — Porta 8002
# =============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI
from typing import Optional, List
import uvicorn

import shared.database as db


# ── Types GraphQL ──────────────────────────────────────────────

@strawberry.type
class User:
    id: int
    nome: str
    idade: int

@strawberry.type
class Song:
    id: int
    nome: str
    artista: str

@strawberry.type
class Playlist:
    id: int
    nome: str
    usuario_id: int
    musicas: List[int]


# ── Inputs GraphQL ─────────────────────────────────────────────

@strawberry.input
class UserInput:
    nome: str
    idade: int

@strawberry.input
class UserUpdateInput:
    nome: Optional[str] = None
    idade: Optional[int] = None

@strawberry.input
class SongInput:
    nome: str
    artista: str

@strawberry.input
class SongUpdateInput:
    nome: Optional[str] = None
    artista: Optional[str] = None

@strawberry.input
class PlaylistInput:
    nome: str
    usuario_id: int
    musicas: Optional[List[int]] = None

@strawberry.input
class PlaylistUpdateInput:
    nome: Optional[str] = None


# ── Helpers de conversão dict → type ──────────────────────────

def to_user(d: dict) -> User:
    return User(id=d["id"], nome=d["nome"], idade=d["idade"])

def to_song(d: dict) -> Song:
    return Song(id=d["id"], nome=d["nome"], artista=d["artista"])

def to_playlist(d: dict) -> Playlist:
    return Playlist(id=d["id"], nome=d["nome"],
                    usuario_id=d["usuario_id"], musicas=d["musicas"])


# ── Queries ────────────────────────────────────────────────────

@strawberry.type
class Query:

    @strawberry.field
    def users(self) -> List[User]:
        return [to_user(u) for u in db.list_users()]

    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        u = db.get_user(id)
        return to_user(u) if u else None

    @strawberry.field
    def user_playlists(self, usuario_id: int) -> List[Playlist]:
        return [to_playlist(p) for p in db.get_user_playlists(usuario_id)]

    @strawberry.field
    def songs(self) -> List[Song]:
        return [to_song(s) for s in db.list_songs()]

    @strawberry.field
    def song(self, id: int) -> Optional[Song]:
        s = db.get_song(id)
        return to_song(s) if s else None

    @strawberry.field
    def song_playlists(self, song_id: int) -> List[Playlist]:
        return [to_playlist(p) for p in db.get_song_playlists(song_id)]

    @strawberry.field
    def playlists(self) -> List[Playlist]:
        return [to_playlist(p) for p in db.list_playlists()]

    @strawberry.field
    def playlist(self, id: int) -> Optional[Playlist]:
        p = db.get_playlist(id)
        return to_playlist(p) if p else None

    @strawberry.field
    def playlist_songs(self, playlist_id: int) -> Optional[List[Song]]:
        songs = db.get_playlist_songs(playlist_id)
        if songs is None:
            return None
        return [to_song(s) for s in songs]


# ── Mutations ──────────────────────────────────────────────────

@strawberry.type
class Mutation:

    # Usuários
    @strawberry.mutation
    def create_user(self, input: UserInput) -> User:
        return to_user(db.create_user(input.nome, input.idade))

    @strawberry.mutation
    def update_user(self, id: int, input: UserUpdateInput) -> Optional[User]:
        u = db.update_user(id, input.nome, input.idade)
        return to_user(u) if u else None

    @strawberry.mutation
    def delete_user(self, id: int) -> bool:
        return db.delete_user(id)

    # Músicas
    @strawberry.mutation
    def create_song(self, input: SongInput) -> Song:
        return to_song(db.create_song(input.nome, input.artista))

    @strawberry.mutation
    def update_song(self, id: int, input: SongUpdateInput) -> Optional[Song]:
        s = db.update_song(id, input.nome, input.artista)
        return to_song(s) if s else None

    @strawberry.mutation
    def delete_song(self, id: int) -> bool:
        return db.delete_song(id)

    # Playlists
    @strawberry.mutation
    def create_playlist(self, input: PlaylistInput) -> Optional[Playlist]:
        p = db.create_playlist(input.nome, input.usuario_id,
                               input.musicas or [])
        return to_playlist(p) if p else None

    @strawberry.mutation
    def update_playlist(self, id: int, input: PlaylistUpdateInput) -> Optional[Playlist]:
        p = db.update_playlist(id, input.nome)
        return to_playlist(p) if p else None

    @strawberry.mutation
    def delete_playlist(self, id: int) -> bool:
        return db.delete_playlist(id)

    @strawberry.mutation
    def add_song_to_playlist(self, playlist_id: int, song_id: int) -> Optional[Playlist]:
        p = db.add_song_to_playlist(playlist_id, song_id)
        return to_playlist(p) if p else None

    @strawberry.mutation
    def remove_song_from_playlist(self, playlist_id: int, song_id: int) -> Optional[Playlist]:
        p = db.remove_song_from_playlist(playlist_id, song_id)
        return to_playlist(p) if p else None


# ── App ────────────────────────────────────────────────────────

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI(title="Music Streaming — GraphQL API")
app.include_router(graphql_app, prefix="/graphql")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
