import { CatalogService } from "../application/catalogService.js";

export const SEED_COUNTS = { users: 200, songs: 400, playlists: 300 };
export function buildCatalogSeed() {
  const service = new CatalogService();
  return { users: service.listUsers(), songs: service.listSongs(), playlists: service.listPlaylists() };
}
