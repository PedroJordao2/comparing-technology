# =============================================================
# Banco de dados em memória compartilhado entre todas as implementações
# =============================================================

from threading import Lock

lock = Lock()

# Contadores de ID automáticos
_counters = {"users": 1, "songs": 1, "playlists": 1}

# Armazenamento principal
users = {}      # id -> {"id", "nome", "idade"}
songs = {}      # id -> {"id", "nome", "artista"}
playlists = {}  # id -> {"id", "nome", "usuario_id", "musicas": []}


def next_id(entity: str) -> int:
    with lock:
        uid = _counters[entity]
        _counters[entity] += 1
        return uid


# ── Helpers de usuário ─────────────────────────────────────────

def create_user(nome: str, idade: int) -> dict:
    uid = next_id("users")
    user = {"id": uid, "nome": nome, "idade": idade}
    with lock:
        users[uid] = user
    return user


def get_user(uid: int) -> dict | None:
    return users.get(uid)


def list_users() -> list:
    return list(users.values())


def update_user(uid: int, nome: str = None, idade: int = None) -> dict | None:
    with lock:
        user = users.get(uid)
        if not user:
            return None
        if nome is not None:
            user["nome"] = nome
        if idade is not None:
            user["idade"] = idade
    return user


def delete_user(uid: int) -> bool:
    with lock:
        if uid not in users:
            return False
        del users[uid]
    return True


def get_user_playlists(uid: int) -> list:
    return [p for p in playlists.values() if p["usuario_id"] == uid]


# ── Helpers de música ──────────────────────────────────────────

def create_song(nome: str, artista: str) -> dict:
    sid = next_id("songs")
    song = {"id": sid, "nome": nome, "artista": artista}
    with lock:
        songs[sid] = song
    return song


def get_song(sid: int) -> dict | None:
    return songs.get(sid)


def list_songs() -> list:
    return list(songs.values())


def update_song(sid: int, nome: str = None, artista: str = None) -> dict | None:
    with lock:
        song = songs.get(sid)
        if not song:
            return None
        if nome is not None:
            song["nome"] = nome
        if artista is not None:
            song["artista"] = artista
    return song


def delete_song(sid: int) -> bool:
    with lock:
        if sid not in songs:
            return False
        del songs[sid]
        # Remove a música de todas as playlists
        for p in playlists.values():
            if sid in p["musicas"]:
                p["musicas"].remove(sid)
    return True


def get_song_playlists(sid: int) -> list:
    return [p for p in playlists.values() if sid in p["musicas"]]


# ── Helpers de playlist ────────────────────────────────────────

def create_playlist(nome: str, usuario_id: int, musicas: list = None) -> dict | None:
    if usuario_id not in users:
        return None
    pid = next_id("playlists")
    playlist = {
        "id": pid,
        "nome": nome,
        "usuario_id": usuario_id,
        "musicas": musicas or []
    }
    with lock:
        playlists[pid] = playlist
    return playlist


def get_playlist(pid: int) -> dict | None:
    return playlists.get(pid)


def list_playlists() -> list:
    return list(playlists.values())


def update_playlist(pid: int, nome: str = None) -> dict | None:
    with lock:
        playlist = playlists.get(pid)
        if not playlist:
            return None
        if nome is not None:
            playlist["nome"] = nome
    return playlist


def delete_playlist(pid: int) -> bool:
    with lock:
        if pid not in playlists:
            return False
        del playlists[pid]
    return True


def add_song_to_playlist(pid: int, sid: int) -> dict | None:
    with lock:
        playlist = playlists.get(pid)
        if not playlist or sid not in songs:
            return None
        if sid not in playlist["musicas"]:
            playlist["musicas"].append(sid)
    return playlist


def remove_song_from_playlist(pid: int, sid: int) -> dict | None:
    with lock:
        playlist = playlists.get(pid)
        if not playlist:
            return None
        if sid in playlist["musicas"]:
            playlist["musicas"].remove(sid)
    return playlist


def get_playlist_songs(pid: int) -> list | None:
    playlist = playlists.get(pid)
    if not playlist:
        return None
    return [songs[sid] for sid in playlist["musicas"] if sid in songs]


# ── Seed: dados iniciais para testes ──────────────────────────

def seed():
    u1 = create_user("Alice", 25)
    u2 = create_user("Bob", 30)
    s1 = create_song("Bohemian Rhapsody", "Queen")
    s2 = create_song("Hotel California", "Eagles")
    s3 = create_song("Stairway to Heaven", "Led Zeppelin")
    create_playlist("Favoritas da Alice", u1["id"], [s1["id"], s2["id"]])
    create_playlist("Rock Clássico", u2["id"], [s2["id"], s3["id"]])


seed()
