import grpc from "@grpc/grpc-js";
import protoLoader from "@grpc/proto-loader";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import { GRPC_PORT } from "../../../config.js";
import { CatalogDomainError, CatalogService } from "../../application/catalogService.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROTO_PATH = resolve(__dirname, "../../../../../proto/music.proto");

const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: false,
  oneofs: true
});
const proto = grpc.loadPackageDefinition(packageDefinition).music.streaming.v1;
const store = new CatalogService();

function grpcStatus(error) {
  if (error instanceof CatalogDomainError) {
    return error.status === 404 ? grpc.status.NOT_FOUND : grpc.status.INVALID_ARGUMENT;
  }
  return grpc.status.INTERNAL;
}

function callbackError(callback, error) {
  callback({
    code: grpcStatus(error),
    message: error.message || "Erro inesperado"
  });
}

function compact(data) {
  return Object.fromEntries(
    Object.entries(data).filter(([, value]) => {
      if (Array.isArray(value)) {
        return value.length > 0;
      }
      return value !== "" && value !== 0 && value !== null && value !== undefined;
    })
  );
}

function unary(handler) {
  return (call, callback) => {
    try {
      callback(null, handler(call.request || {}));
    } catch (error) {
      callbackError(callback, error);
    }
  };
}

function songInput(request) {
  return {
    title: request.title,
    artist: request.artist,
    album: request.album,
    durationSeconds: request.duration_seconds
  };
}

function playlistInput(request) {
  return {
    userId: request.user_id,
    name: request.name,
    songIds: request.song_ids || []
  };
}

const handlers = {
  Reset: unary(() => store.reset()),
  ListUsers: unary(() => ({ users: store.listUsers() })),
  GetUser: unary((request) => store.getUser(request.id)),
  CreateUser: unary((request) => store.createUser(request)),
  UpdateUser: unary((request) => store.updateUser(request.id, compact(request.user || {}))),
  DeleteUser: unary((request) => store.deleteUser(request.id)),
  ListSongs: unary(() => ({ songs: store.listSongs() })),
  GetSong: unary((request) => store.getSong(request.id)),
  CreateSong: unary((request) => store.createSong(songInput(request))),
  UpdateSong: unary((request) => store.updateSong(request.id, compact(request.song || {}))),
  DeleteSong: unary((request) => store.deleteSong(request.id)),
  ListPlaylists: unary((request) => ({
    playlists: store.listPlaylists(compact({ userId: request.user_id, songId: request.song_id }))
  })),
  GetPlaylist: unary((request) => store.getPlaylist(request.id)),
  CreatePlaylist: unary((request) => store.createPlaylist(playlistInput(request))),
  UpdatePlaylist: unary((request) => store.updatePlaylist(request.id, compact(request.playlist || {}))),
  DeletePlaylist: unary((request) => store.deletePlaylist(request.id)),
  ListUserPlaylists: unary((request) => ({ playlists: store.listUserPlaylists(request.user_id) })),
  ListPlaylistSongs: unary((request) => ({ songs: store.listPlaylistSongs(request.playlist_id) })),
  ListSongPlaylists: unary((request) => ({ playlists: store.listSongPlaylists(request.song_id) }))
};

const server = new grpc.Server();
server.addService(proto.MusicCatalogService.service, handlers);
server.bindAsync(`0.0.0.0:${GRPC_PORT}`, grpc.ServerCredentials.createInsecure(), (error, port) => {
  if (error) {
    console.error(error);
    process.exit(1);
  }
  console.log(`gRPC JavaScript ouvindo em 0.0.0.0:${port}`);
});


