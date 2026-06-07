# =============================================================
# Servidor gRPC — Porta 50051
# Para gerar os stubs, rode na pasta grpc_service/:
#   python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. music.proto
# =============================================================

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import grpc
from concurrent import futures
import time

# Stubs gerados automaticamente pelo protoc
import music_pb2 as pb
import music_pb2_grpc as pb_grpc

import shared.database as db


# ── Conversores dict → proto ───────────────────────────────────

def dict_to_user(d: dict) -> pb.User:
    return pb.User(id=d["id"], nome=d["nome"], idade=d["idade"])

def dict_to_song(d: dict) -> pb.Song:
    return pb.Song(id=d["id"], nome=d["nome"], artista=d["artista"])

def dict_to_playlist(d: dict) -> pb.Playlist:
    return pb.Playlist(id=d["id"], nome=d["nome"],
                       usuario_id=d["usuario_id"], musicas=d["musicas"])


# ── Implementação UserService ──────────────────────────────────

class UserServicer(pb_grpc.UserServiceServicer):

    def CreateUser(self, request, context):
        user = db.create_user(request.nome, request.idade)
        return dict_to_user(user)

    def ListUsers(self, request, context):
        users = [dict_to_user(u) for u in db.list_users()]
        return pb.UserList(users=users)

    def GetUser(self, request, context):
        user = db.get_user(request.id)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Usuário não encontrado")
            return pb.User()
        return dict_to_user(user)

    def UpdateUser(self, request, context):
        nome = request.nome if request.nome else None
        idade = request.idade if request.idade else None
        user = db.update_user(request.id, nome, idade)
        if not user:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Usuário não encontrado")
            return pb.User()
        return dict_to_user(user)

    def DeleteUser(self, request, context):
        return pb.BoolResponse(success=db.delete_user(request.id))

    def GetUserPlaylists(self, request, context):
        playlists = [dict_to_playlist(p)
                     for p in db.get_user_playlists(request.usuario_id)]
        return pb.PlaylistList(playlists=playlists)


# ── Implementação SongService ──────────────────────────────────

class SongServicer(pb_grpc.SongServiceServicer):

    def CreateSong(self, request, context):
        song = db.create_song(request.nome, request.artista)
        return dict_to_song(song)

    def ListSongs(self, request, context):
        songs = [dict_to_song(s) for s in db.list_songs()]
        return pb.SongList(songs=songs)

    def GetSong(self, request, context):
        song = db.get_song(request.id)
        if not song:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Música não encontrada")
            return pb.Song()
        return dict_to_song(song)

    def UpdateSong(self, request, context):
        nome = request.nome if request.nome else None
        artista = request.artista if request.artista else None
        song = db.update_song(request.id, nome, artista)
        if not song:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Música não encontrada")
            return pb.Song()
        return dict_to_song(song)

    def DeleteSong(self, request, context):
        return pb.BoolResponse(success=db.delete_song(request.id))

    def GetSongPlaylists(self, request, context):
        playlists = [dict_to_playlist(p)
                     for p in db.get_song_playlists(request.song_id)]
        return pb.PlaylistList(playlists=playlists)


# ── Implementação PlaylistService ──────────────────────────────

class PlaylistServicer(pb_grpc.PlaylistServiceServicer):

    def CreatePlaylist(self, request, context):
        playlist = db.create_playlist(request.nome, request.usuario_id,
                                      list(request.musicas))
        if not playlist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Usuário não encontrado")
            return pb.Playlist()
        return dict_to_playlist(playlist)

    def ListPlaylists(self, request, context):
        playlists = [dict_to_playlist(p) for p in db.list_playlists()]
        return pb.PlaylistList(playlists=playlists)

    def GetPlaylist(self, request, context):
        playlist = db.get_playlist(request.id)
        if not playlist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist não encontrada")
            return pb.Playlist()
        return dict_to_playlist(playlist)

    def UpdatePlaylist(self, request, context):
        nome = request.nome if request.nome else None
        playlist = db.update_playlist(request.id, nome)
        if not playlist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist não encontrada")
            return pb.Playlist()
        return dict_to_playlist(playlist)

    def DeletePlaylist(self, request, context):
        return pb.BoolResponse(success=db.delete_playlist(request.id))

    def AddSongToPlaylist(self, request, context):
        playlist = db.add_song_to_playlist(request.playlist_id, request.song_id)
        if not playlist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist ou música não encontrada")
            return pb.Playlist()
        return dict_to_playlist(playlist)

    def RemoveSongFromPlaylist(self, request, context):
        playlist = db.remove_song_from_playlist(request.playlist_id, request.song_id)
        if not playlist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist não encontrada")
            return pb.Playlist()
        return dict_to_playlist(playlist)

    def GetPlaylistSongs(self, request, context):
        songs = db.get_playlist_songs(request.id)
        if songs is None:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Playlist não encontrada")
            return pb.SongList()
        return pb.SongList(songs=[dict_to_song(s) for s in songs])


# ── Main ───────────────────────────────────────────────────────

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pb_grpc.add_UserServiceServicer_to_server(UserServicer(), server)
    pb_grpc.add_SongServiceServicer_to_server(SongServicer(), server)
    pb_grpc.add_PlaylistServiceServicer_to_server(PlaylistServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC server rodando na porta 50051...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve()
