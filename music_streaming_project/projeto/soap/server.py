# =============================================================
# Servidor SOAP — Spyne — Porta 8003
# WSDL disponível em: http://localhost:8003/?wsdl
# =============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from spyne import Application, rpc, Service, Integer, Unicode, Array, Boolean
from spyne.model import ComplexModel
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server

import shared.database as db


# ── Modelos Spyne ──────────────────────────────────────────────

class UserModel(ComplexModel):
    id     = Integer
    nome   = Unicode
    idade  = Integer

class SongModel(ComplexModel):
    id      = Integer
    nome    = Unicode
    artista = Unicode

class PlaylistModel(ComplexModel):
    id         = Integer
    nome       = Unicode
    usuario_id = Integer
    musicas    = Array(Integer)


# ── Helpers de conversão ───────────────────────────────────────

def to_user_model(d: dict) -> UserModel:
    u = UserModel()
    u.id = d["id"]; u.nome = d["nome"]; u.idade = d["idade"]
    return u

def to_song_model(d: dict) -> SongModel:
    s = SongModel()
    s.id = d["id"]; s.nome = d["nome"]; s.artista = d["artista"]
    return s

def to_playlist_model(d: dict) -> PlaylistModel:
    p = PlaylistModel()
    p.id = d["id"]; p.nome = d["nome"]
    p.usuario_id = d["usuario_id"]; p.musicas = d["musicas"]
    return p


# ── Serviço de Usuários ────────────────────────────────────────

class UserService(Service):
    __service_url_path__ = "/users"
    __in_protocol__  = Soap11(validator="lxml")
    __out_protocol__ = Soap11()

    @rpc(Unicode, Integer, _returns=UserModel)
    def create_user(ctx, nome, idade):
        return to_user_model(db.create_user(nome, idade))

    @rpc(_returns=Array(UserModel))
    def list_users(ctx):
        return [to_user_model(u) for u in db.list_users()]

    @rpc(Integer, _returns=UserModel)
    def get_user(ctx, id):
        u = db.get_user(id)
        return to_user_model(u) if u else None

    @rpc(Integer, Unicode, Integer, _returns=UserModel)
    def update_user(ctx, id, nome, idade):
        u = db.update_user(id, nome or None, idade or None)
        return to_user_model(u) if u else None

    @rpc(Integer, _returns=Boolean)
    def delete_user(ctx, id):
        return db.delete_user(id)

    @rpc(Integer, _returns=Array(PlaylistModel))
    def get_user_playlists(ctx, usuario_id):
        return [to_playlist_model(p) for p in db.get_user_playlists(usuario_id)]


# ── Serviço de Músicas ─────────────────────────────────────────

class SongService(Service):
    __service_url_path__ = "/songs"
    __in_protocol__  = Soap11(validator="lxml")
    __out_protocol__ = Soap11()

    @rpc(Unicode, Unicode, _returns=SongModel)
    def create_song(ctx, nome, artista):
        return to_song_model(db.create_song(nome, artista))

    @rpc(_returns=Array(SongModel))
    def list_songs(ctx):
        return [to_song_model(s) for s in db.list_songs()]

    @rpc(Integer, _returns=SongModel)
    def get_song(ctx, id):
        s = db.get_song(id)
        return to_song_model(s) if s else None

    @rpc(Integer, Unicode, Unicode, _returns=SongModel)
    def update_song(ctx, id, nome, artista):
        s = db.update_song(id, nome or None, artista or None)
        return to_song_model(s) if s else None

    @rpc(Integer, _returns=Boolean)
    def delete_song(ctx, id):
        return db.delete_song(id)

    @rpc(Integer, _returns=Array(PlaylistModel))
    def get_song_playlists(ctx, song_id):
        return [to_playlist_model(p) for p in db.get_song_playlists(song_id)]


# ── Serviço de Playlists ───────────────────────────────────────

class PlaylistService(Service):
    __service_url_path__ = "/playlists"
    __in_protocol__  = Soap11(validator="lxml")
    __out_protocol__ = Soap11()

    @rpc(Unicode, Integer, Array(Integer), _returns=PlaylistModel)
    def create_playlist(ctx, nome, usuario_id, musicas):
        p = db.create_playlist(nome, usuario_id, musicas or [])
        return to_playlist_model(p) if p else None

    @rpc(_returns=Array(PlaylistModel))
    def list_playlists(ctx):
        return [to_playlist_model(p) for p in db.list_playlists()]

    @rpc(Integer, _returns=PlaylistModel)
    def get_playlist(ctx, id):
        p = db.get_playlist(id)
        return to_playlist_model(p) if p else None

    @rpc(Integer, Unicode, _returns=PlaylistModel)
    def update_playlist(ctx, id, nome):
        p = db.update_playlist(id, nome or None)
        return to_playlist_model(p) if p else None

    @rpc(Integer, _returns=Boolean)
    def delete_playlist(ctx, id):
        return db.delete_playlist(id)

    @rpc(Integer, Integer, _returns=PlaylistModel)
    def add_song_to_playlist(ctx, playlist_id, song_id):
        p = db.add_song_to_playlist(playlist_id, song_id)
        return to_playlist_model(p) if p else None

    @rpc(Integer, Integer, _returns=PlaylistModel)
    def remove_song_from_playlist(ctx, playlist_id, song_id):
        p = db.remove_song_from_playlist(playlist_id, song_id)
        return to_playlist_model(p) if p else None

    @rpc(Integer, _returns=Array(SongModel))
    def get_playlist_songs(ctx, id):
        songs = db.get_playlist_songs(id)
        if songs is None:
            return []
        return [to_song_model(s) for s in songs]


# ── App WSGI ───────────────────────────────────────────────────

application = Application(
    [UserService, SongService, PlaylistService],
    tns="music.streaming",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11(),
)

wsgi_app = WsgiApplication(application)

if __name__ == "__main__":
    server = make_server("0.0.0.0", 8003, wsgi_app)
    print("SOAP server rodando na porta 8003...")
    print("WSDL disponível em: http://localhost:8003/?wsdl")
    server.serve_forever()
