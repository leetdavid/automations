"""
Sync Monster Siren Records tracks to a Spotify playlist.

Fetches all tracks from the Monster Siren Records artist and adds any that
aren't already in the target playlist. Designed to run weekly via GitHub Actions.

Required env vars:
  SPOTIFY_CLIENT_ID
  SPOTIFY_CLIENT_SECRET
  SPOTIFY_REFRESH_TOKEN
"""

import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

ARTIST_ID = "7l5zSPffvPDaRRYkAHsyt7"
PLAYLIST_ID = "4hsMCsQm0FMXa7ek5FfumW"
SCOPE = "playlist-modify-public playlist-modify-private"


def get_spotify_client() -> spotipy.Spotify:
    auth_manager = SpotifyOAuth(
        client_id=os.environ["SPOTIFY_CLIENT_ID"],
        client_secret=os.environ["SPOTIFY_CLIENT_SECRET"],
        redirect_uri="http://127.0.0.1:8888/callback",
        scope=SCOPE,
    )
    # Inject the refresh token so no browser flow is needed in CI
    token_info = auth_manager.refresh_access_token(os.environ["SPOTIFY_REFRESH_TOKEN"])
    return spotipy.Spotify(auth=token_info["access_token"])


def get_all_artist_track_uris(sp: spotipy.Spotify) -> set[str]:
    """Return all track URIs from every album/single/EP by the artist."""
    track_uris: set[str] = set()

    # Fetch all albums (includes albums, singles, compilations)
    album_ids: list[str] = []
    result = sp.artist_albums(ARTIST_ID, album_type="album,single,compilation", limit=50)
    while result:
        for album in result["items"]:
            album_ids.append(album["id"])
        result = sp.next(result) if result["next"] else None

    # Fetch all tracks from each album
    for album_id in album_ids:
        result = sp.album_tracks(album_id, limit=50)
        while result:
            for track in result["items"]:
                track_uris.add(track["uri"])
            result = sp.next(result) if result["next"] else None

    return track_uris


def get_playlist_track_uris(sp: spotipy.Spotify) -> set[str]:
    """Return all track URIs currently in the playlist."""
    track_uris: set[str] = set()
    result = sp.playlist_tracks(PLAYLIST_ID, fields="items(track(uri)),next", limit=100)
    while result:
        for item in result["items"]:
            if item["track"] and item["track"]["uri"]:
                track_uris.add(item["track"]["uri"])
        result = sp.next(result) if result["next"] else None
    return track_uris


def add_tracks_in_batches(sp: spotipy.Spotify, uris: list[str]) -> None:
    """Add tracks to the playlist in batches of 100 (Spotify API limit)."""
    for i in range(0, len(uris), 100):
        sp.playlist_add_items(PLAYLIST_ID, uris[i : i + 100])


def main() -> None:
    sp = get_spotify_client()

    print("Fetching artist tracks...")
    artist_tracks = get_all_artist_track_uris(sp)
    print(f"  Found {len(artist_tracks)} tracks from Monster Siren Records")

    print("Fetching playlist tracks...")
    playlist_tracks = get_playlist_track_uris(sp)
    print(f"  Found {len(playlist_tracks)} tracks in playlist")

    new_tracks = list(artist_tracks - playlist_tracks)
    if not new_tracks:
        print("Already up to date — no new tracks to add.")
        return

    print(f"Adding {len(new_tracks)} new track(s)...")
    add_tracks_in_batches(sp, new_tracks)
    print(f"Done. Added {len(new_tracks)} track(s) to the playlist.")


if __name__ == "__main__":
    main()
