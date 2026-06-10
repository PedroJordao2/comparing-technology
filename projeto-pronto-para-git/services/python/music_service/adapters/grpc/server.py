from concurrent import futures

import grpc

from music_service.config import GRPC_PORT
from music_service.application.catalog_service import CatalogDomainError, CatalogService
from music_service.generated import music_pb2, music_pb2_grpc


store = CatalogService()


def user_message(user):
    return music_pb2.UserRecord(id=user["id"], name=user["name"], email=user["email"])


def song_message(song):
    return music_pb2.SongRecord(
        id=song["id"],
        title=song["title"],
        artist=song["artist"],
        album=song["album"],
        duration_seconds=song["durationSeconds"],
    )


def playlist_message(playlist):
    return music_pb2.PlaylistRecord(
        id=playlist["id"],
        user_id=playlist["userId"],
        name=playlist["name"],
        song_ids=playlist["songIds"],
    )


def mutation_result(result):
    return music_pb2.MutationResult(ok=bool(result.get("ok")))


def compact(data):
    return {
        key: value
        for key, value in data.items()
        if value not in ("", 0, [], None)
    }


def user_input(request):
    return {"name": request.name, "email": request.email}


def song_input(request):
    return {
        "title": request.title,
        "artist": request.artist,
        "album": request.album,
        "durationSeconds": request.duration_seconds,
    }


def playlist_input(request):
    return {
        "userId": request.user_id,
        "name": request.name,
        "songIds": list(request.song_ids),
    }


def user_patch(request):
    return compact({"name": request.name, "email": request.email})


def song_patch(request):
    return compact({
        "title": request.title,
        "artist": request.artist,
        "album": request.album,
        "durationSeconds": request.duration_seconds,
    })


def playlist_patch(request):
    return compact({
        "userId": request.user_id,
        "name": request.name,
        "songIds": list(request.song_ids),
    })


def grpc_error(error, context):
    if isinstance(error, CatalogDomainError):
        context.set_code(grpc.StatusCode.NOT_FOUND if error.status == 404 else grpc.StatusCode.INVALID_ARGUMENT)
    else:
        context.set_code(grpc.StatusCode.INTERNAL)
    context.set_details(str(error) or "Erro inesperado")


class MusicCatalogGrpcAdapter(music_pb2_grpc.MusicCatalogServiceServicer):
    def Reset(self, request, context):
        try:
            return mutation_result(store.reset())
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.MutationResult()

    def ListUsers(self, request, context):
        try:
            return music_pb2.UserListResponse(users=[user_message(user) for user in store.list_users()])
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.UserListResponse()

    def GetUser(self, request, context):
        try:
            return user_message(store.get_user(request.id))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.UserRecord()

    def CreateUser(self, request, context):
        try:
            return user_message(store.create_user(user_input(request)))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.UserRecord()

    def UpdateUser(self, request, context):
        try:
            return user_message(store.update_user(request.id, user_patch(request.user)))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.UserRecord()

    def DeleteUser(self, request, context):
        try:
            return mutation_result(store.delete_user(request.id))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.MutationResult()

    def ListSongs(self, request, context):
        try:
            return music_pb2.SongListResponse(songs=[song_message(song) for song in store.list_songs()])
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.SongListResponse()

    def GetSong(self, request, context):
        try:
            return song_message(store.get_song(request.id))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.SongRecord()

    def CreateSong(self, request, context):
        try:
            return song_message(store.create_song(song_input(request)))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.SongRecord()

    def UpdateSong(self, request, context):
        try:
            return song_message(store.update_song(request.id, song_patch(request.song)))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.SongRecord()

    def DeleteSong(self, request, context):
        try:
            return mutation_result(store.delete_song(request.id))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.MutationResult()

    def ListPlaylists(self, request, context):
        try:
            filters = compact({"userId": request.user_id, "songId": request.song_id})
            return music_pb2.PlaylistListResponse(
                playlists=[playlist_message(playlist) for playlist in store.list_playlists(filters)]
            )
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.PlaylistListResponse()

    def GetPlaylist(self, request, context):
        try:
            return playlist_message(store.get_playlist(request.id))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.PlaylistRecord()

    def CreatePlaylist(self, request, context):
        try:
            return playlist_message(store.create_playlist(playlist_input(request)))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.PlaylistRecord()

    def UpdatePlaylist(self, request, context):
        try:
            return playlist_message(store.update_playlist(request.id, playlist_patch(request.playlist)))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.PlaylistRecord()

    def DeletePlaylist(self, request, context):
        try:
            return mutation_result(store.delete_playlist(request.id))
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.MutationResult()

    def ListUserPlaylists(self, request, context):
        try:
            return music_pb2.PlaylistListResponse(
                playlists=[playlist_message(playlist) for playlist in store.list_user_playlists(request.user_id)]
            )
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.PlaylistListResponse()

    def ListPlaylistSongs(self, request, context):
        try:
            return music_pb2.SongListResponse(
                songs=[song_message(song) for song in store.list_playlist_songs(request.playlist_id)]
            )
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.SongListResponse()

    def ListSongPlaylists(self, request, context):
        try:
            return music_pb2.PlaylistListResponse(
                playlists=[playlist_message(playlist) for playlist in store.list_song_playlists(request.song_id)]
            )
        except Exception as error:
            grpc_error(error, context)
            return music_pb2.PlaylistListResponse()


def create_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=64))
    music_pb2_grpc.add_MusicCatalogServiceServicer_to_server(MusicCatalogGrpcAdapter(), server)
    bound_port = server.add_insecure_port(f"0.0.0.0:{GRPC_PORT}")
    if bound_port == 0:
        raise RuntimeError(f"Nao foi possivel abrir a porta gRPC {GRPC_PORT}")
    return server


def main():
    server = create_server()
    server.start()
    print(f"gRPC ouvindo em 0.0.0.0:{GRPC_PORT}", flush=True)
    server.wait_for_termination()


if __name__ == "__main__":
    main()


