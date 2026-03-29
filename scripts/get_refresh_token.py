"""
One-time script to obtain a Spotify refresh token.

Starts a local HTTP server on port 8888 to automatically catch the OAuth
callback, then exchanges the code for tokens and prints the refresh token.

Usage:
  1. Copy .env.example to .env and fill in SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET
  2. uv run scripts/get_refresh_token.py
  3. A browser window will open — log in and authorize the app
  4. The refresh token will be printed automatically — save it as SPOTIFY_REFRESH_TOKEN
"""

import os
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ["SPOTIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SPOTIFY_CLIENT_SECRET"]
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "playlist-modify-public playlist-modify-private"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

# Will be set by the callback handler
_auth_code: str | None = None


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _auth_code
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if "code" in params:
            _auth_code = params["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h2>Authorized! You can close this tab.</h2>")
        else:
            error = params.get("error", ["unknown"])[0]
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(f"<h2>Authorization failed: {error}</h2>".encode())

    def log_message(self, format, *args):
        pass  # silence request logs


def get_auth_url() -> str:
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def exchange_code_for_tokens(code: str) -> dict:
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        },
        auth=(CLIENT_ID, CLIENT_SECRET),
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    auth_url = get_auth_url()
    print("Opening Spotify authorization page in your browser...")
    print(f"  {auth_url}\n")
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 8888), CallbackHandler)
    print("Waiting for authorization callback on http://localhost:8888 ...")
    server.handle_request()  # handles exactly one request then stops

    if not _auth_code:
        print("Authorization failed — no code received.")
        raise SystemExit(1)

    tokens = exchange_code_for_tokens(_auth_code)

    print("\nRefresh token (save this as the SPOTIFY_REFRESH_TOKEN GitHub secret):")
    print(tokens["refresh_token"])


if __name__ == "__main__":
    main()
