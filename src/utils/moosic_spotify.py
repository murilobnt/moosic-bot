import os
import json
import requests

from spotipy.oauth2 import SpotifyClientCredentials
from bs4 import BeautifulSoup

class MoosicSpotify:
    def __init__(self):
        self.sp_auth = SpotifyClientCredentials(client_id=os.environ.get("SP_CLIENT"), client_secret=os.environ.get("SP_SECRET"))

    def get_album_tracks(self, spotify_id):
        headers={"Authorization": f"Bearer {self.sp_auth.get_access_token(as_dict=False)}"}
        response = requests.get(f"https://api.spotify.com/v1/albums/{spotify_id}/tracks", headers=headers)
        return response.json().get("items")

    def get_track(self, spotify_id):
        headers={"Authorization": f"Bearer {self.sp_auth.get_access_token(as_dict=False)}"}
        response = requests.get(f"https://api.spotify.com/v1/tracks/{spotify_id}", headers=headers)
        return response.json()

    def get_playlist_tracks(self, spotify_id):
        headers={"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "DNT": "1"}
        response = requests.get(f"https://open.spotify.com/embed/playlist/{spotify_id}", headers=headers)

        html_data = response.text
        bsoup = BeautifulSoup(html_data, "html.parser")
        next_data = bsoup.select_one("script#__NEXT_DATA__")
        json_data = json.loads(next_data.string)
        return json_data["props"]["pageProps"]["state"]["data"]["entity"]["trackList"]
