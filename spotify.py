from threading import Event, Thread, Timer
from time import sleep
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
import yaml
from pathlib import Path
from pprint import pprint
from urllib.parse import urlparse
import logging


log = logging.getLogger()
basePath = Path(__file__).parent
cachePath = basePath / ".cache"


class PlaylistAdder:
    def __init__(self, client_id: str, client_secret: str, playlist: str) -> None:
        self.default_playlist = playlist
        self.client_id = client_id
        self.client_secret = client_secret

        self.authenticate()
        self.stop_event = Event()
        self.refresh_thread = Thread(target=self.refresh_token)
        self.refresh_thread.start()

    def authenticate(self):
        redirectUrl = "https://example.com/callback"
        scope = " ".join(
            [
                "playlist-modify-private",
                "playlist-modify-public",
            ]
        )

        self.auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=redirectUrl,
            scope=scope,
            cache_path=cachePath,
        )
        self.user = spotipy.Spotify(auth_manager=self.auth_manager)

        self.sp = spotipy.Spotify(
            client_credentials_manager=SpotifyClientCredentials(
                client_id=self.client_id, client_secret=self.client_secret
            )
        )

    def stop(self):
        self.stop_event.set()

    def refresh_token(self):
        while not self.stop_event.is_set():
            sleep(30 * 60)
            log.warning("refeshing token")
            token_info = self.auth_manager.cache_handler.get_cached_token()
            self.auth_manager.refresh_access_token(token_info["refresh_token"])

    def add_to_playlist(self, url: str):
        o = urlparse(url)
        if not o.hostname == "open.spotify.com":
            # TODO add support for spotify.link shortlinks
            # or (o.hostname == "spotify.link")
            return False

        if o.path.startswith("/track"):
            track = self.sp.track(url)
            if track is not None:
                self.user.playlist_add_items(self.default_playlist, [track["uri"]], 0)
                return True
        elif o.path.startswith("/album"):
            album = self.sp.album_tracks(url)
            # TODO do something interesting with it
        elif o.path.startswith("/artist"):
            # idfk man
            pass
        return False


if __name__ == "__main__":
    with open(Path(__file__).parent / "config.yml") as f:
        conf = yaml.safe_load(f)

    pa = PlaylistAdder(
        conf["spotify_client_id"],
        conf["spotify_client_secret"],
        conf["default_playlist"],
    )
