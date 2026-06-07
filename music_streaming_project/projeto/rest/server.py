# =============================================================
# Servidor REST — FastAPI — Porta 8001
# =============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import uvicorn

import shared.database as db

app = FastAPI(title="Music Streaming — REST API")


# ── Schemas de entrada ─────────────────────────────────────────

class UserCreate(BaseModel):
    nome: str
    idade: int

class UserUpdate(BaseModel):
    nome: Optional[str] = None
    idade: Optional[int] = None

class SongCreate(BaseModel):
    nome: str
    artista: str

class SongUpdate(BaseModel):
    nome: Optional[str] = None
    artista: Optional[str] = None

class PlaylistCreate(BaseModel):
    nome: str
    usuario_id: int
    musicas: Optional[List[int]] = []

class PlaylistUpdate(BaseModel):
    nome: Optional[str] = None


# ── Rotas de Usuário ───────────────────────────────────────────

@app.post("/users", status_code=201)
def create_user(body: UserCreate):
    return db.create_user(body.nome, body.idade)

@app.get("/users")
def list_users():
    return db.list_users()

@app.get("/users/{uid}")
def get_user(uid: int):
    user = db.get_user(uid)
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    return user

@app.put("/users/{uid}")
def update_user(uid: int, body: UserUpdate):
    user = db.update_user(uid, body.nome, body.idade)
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    return user

@app.delete("/users/{uid}", status_code=204)
def delete_user(uid: int):
    if not db.delete_user(uid):
        raise HTTPException(404, "Usuário não encontrado")

@app.get("/users/{uid}/playlists")
def get_user_playlists(uid: int):
    if not db.get_user(uid):
        raise HTTPException(404, "Usuário não encontrado")
    return db.get_user_playlists(uid)


# ── Rotas de Música ────────────────────────────────────────────

@app.post("/songs", status_code=201)
def create_song(body: SongCreate):
    return db.create_song(body.nome, body.artista)

@app.get("/songs")
def list_songs():
    return db.list_songs()

@app.get("/songs/{sid}")
def get_song(sid: int):
    song = db.get_song(sid)
    if not song:
        raise HTTPException(404, "Música não encontrada")
    return song

@app.put("/songs/{sid}")
def update_song(sid: int, body: SongUpdate):
    song = db.update_song(sid, body.nome, body.artista)
    if not song:
        raise HTTPException(404, "Música não encontrada")
    return song

@app.delete("/songs/{sid}", status_code=204)
def delete_song(sid: int):
    if not db.delete_song(sid):
        raise HTTPException(404, "Música não encontrada")

@app.get("/songs/{sid}/playlists")
def get_song_playlists(sid: int):
    if not db.get_song(sid):
        raise HTTPException(404, "Música não encontrada")
    return db.get_song_playlists(sid)


# ── Rotas de Playlist ──────────────────────────────────────────

@app.post("/playlists", status_code=201)
def create_playlist(body: PlaylistCreate):
    playlist = db.create_playlist(body.nome, body.usuario_id, body.musicas)
    if not playlist:
        raise HTTPException(404, "Usuário não encontrado")
    return playlist

@app.get("/playlists")
def list_playlists():
    return db.list_playlists()

@app.get("/playlists/{pid}")
def get_playlist(pid: int):
    playlist = db.get_playlist(pid)
    if not playlist:
        raise HTTPException(404, "Playlist não encontrada")
    return playlist

@app.put("/playlists/{pid}")
def update_playlist(pid: int, body: PlaylistUpdate):
    playlist = db.update_playlist(pid, body.nome)
    if not playlist:
        raise HTTPException(404, "Playlist não encontrada")
    return playlist

@app.delete("/playlists/{pid}", status_code=204)
def delete_playlist(pid: int):
    if not db.delete_playlist(pid):
        raise HTTPException(404, "Playlist não encontrada")

@app.post("/playlists/{pid}/songs/{sid}")
def add_song_to_playlist(pid: int, sid: int):
    playlist = db.add_song_to_playlist(pid, sid)
    if not playlist:
        raise HTTPException(404, "Playlist ou música não encontrada")
    return playlist

@app.delete("/playlists/{pid}/songs/{sid}")
def remove_song_from_playlist(pid: int, sid: int):
    playlist = db.remove_song_from_playlist(pid, sid)
    if not playlist:
        raise HTTPException(404, "Playlist não encontrada")
    return playlist

@app.get("/playlists/{pid}/songs")
def get_playlist_songs(pid: int):
    songs = db.get_playlist_songs(pid)
    if songs is None:
        raise HTTPException(404, "Playlist não encontrada")
    return songs


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
