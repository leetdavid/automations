# automations

Personal automations running on GitHub Actions.

---

## Monster Siren Records → Spotify Playlist

Runs every **Sunday at 9am HKT**, fetches all tracks from [Monster Siren Records](https://open.spotify.com/artist/7l5zSPffvPDaRRYkAHsyt7) on Spotify, and adds any new ones to [my playlist](https://open.spotify.com/playlist/4hsMCsQm0FMXa7ek5FfumW).

### One-time setup

#### 1. Create a Spotify app

1. Go to [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) and create an app.
2. Add `http://localhost:8888/callback` as a Redirect URI in the app settings.
3. Note your **Client ID** and **Client Secret**.

#### 2. Get a refresh token

```bash
cp .env.example .env
# Fill in SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env

uv run scripts/get_refresh_token.py
# A browser window will open — log in and authorize
# Copy the refresh token printed to the terminal
```

#### 3. Add GitHub Secrets

In your repo → **Settings → Secrets and variables → Actions**, add:

| Secret | Value |
|--------|-------|
| `SPOTIFY_CLIENT_ID` | From your Spotify app |
| `SPOTIFY_CLIENT_SECRET` | From your Spotify app |
| `SPOTIFY_REFRESH_TOKEN` | From step 2 |

### Running manually

Trigger a run anytime from **Actions → Monster Siren Records Sync → Run workflow**.

### Running locally

```bash
cp .env.example .env  # fill in all three values
uv run scripts/sync_monster_siren.py
```
