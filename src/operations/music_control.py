import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import datetime
import os
import re
import time
import random

from urllib.parse import urlparse

from src.utils.helpers import Helpers
from src.utils.moosic_finder import MoosicFinder
from src.utils.moosic_grabber import MoosicGrabber
from src.utils.translator import Translator
from src.utils.moosic_error import MoosicError

from src.utils.enums import LoopState

class Seeker:
    def __init__(self):
        self.on_seek = False
        self.seek_options = ""
        self.gap = 0

    def seek(self, timestamp):
        if not re.match('^((?:\d{1,2}:)?(?:\d{1,2}:)?(?:\d{1,2})|\d+)$', timestamp):
            raise MoosicError("er_seekarg")

        self.on_seek = True
        self.seek_options = f"-ss {timestamp}"
        self.gap = Helpers.get_gap_from_timestamp(timestamp)

class MusicControl:
    def __init__(self):
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=os.environ["SP_CLIENT"], client_secret=os.environ["SP_SECRET"]))
        self.seeker = Seeker()

        self.music_list = []
        self.current_index = 0
        self.elapsed_timestamp = None
        self.paused_timestamp = None
        self.loop_state = LoopState.NOT_ON_LOOP

        self.playing = False
        self.jump = False

    def add_youtube_song(self, youtube_url):
        try:
            video_id = Helpers.get_youtube_url_id(youtube_url)
            video_info = MoosicGrabber.request_yt(video_id)
            song = MoosicFinder.gen_youtube_song_url(video_info)
            self.music_list.append(song)
            return song
        except:
            raise MoosicError("er_himalformed")

    def add_youtube_shorts_song(self, youtube_url):
        try:
            parsed_url = urlparse(youtube_url)
            video_id = parsed_url.path.split("/")[2]
            video_info = MoosicGrabber.request_yt(video_id)
            song = MoosicFinder.gen_youtube_song_url(video_info)
            self.music_list.append(song)
            return song
        except:
            raise MoosicError("er_himalformed")

    def add_youtube_search(self, info):
        song = MoosicFinder.gen_youtube_song_search(info)
        self.music_list.append(song)
        return song

    def add_youtube_playlist(self, youtube_url):
        fetch_pl = MoosicFinder.fetch_yt_playlist(youtube_url)
        pl = MoosicFinder.gen_youtube_playlist(fetch_pl)
        self.music_list.extend(pl)
        return len(pl)

    def add_spotify_song(self, spotify_url):
        track_URI = spotify_url.split("/")[-1].split("?")[0]
        track = self.sp.track(track_URI)
        song = MoosicFinder.gen_spotify_song(track)
        self.music_list.append(song)
        return song

    def add_spotify_album(self, spotify_url):
        playlist_URI = spotify_url.split("/")[-1].split("?")[0]
        try:
            tracks_uri = self.sp.playlist_tracks(playlist_URI)["items"]
        except:
            tracks_uri = self.sp.album_tracks(playlist_URI)["items"]
        pl = MoosicFinder.gen_spotify_playlist(tracks_uri)
        self.music_list.extend(pl)
        return len(pl)

    def pause(self):
        if self.paused_timestamp:
            raise MoosicError("er_paused")

        self.paused_timestamp = time.time()

    def resume(self):
        if not self.paused_timestamp:
            raise MoosicError("er_nopause")

        self.elapsed_timestamp = self.elapsed_timestamp + (time.time() - self.paused_timestamp)
        self.paused_timestamp = None

    def play(self):
        self.elapsed_timestamp = time.time() if not self.seeker.on_seek else time.time() - self.seeker.gap

    def get_current_song(self):
        return self.music_list[self.current_index]

    def skip(self, n = 1):
        if n > len(self.music_list) - self.current_index:
            n = len(self.music_list) - self.current_index

        self.current_index += n - 1 

    def remove(self, index):
        if index >= len(self.music_list):
            raise MoosicError("er_rmindex")

        if self.loop_state == LoopState.LOOP_TRACK:
            if index < self.current_index:
                self.current_index -= 1
        else:
            if index <= self.current_index:
                self.current_index -= 1

        self.music_list.pop(index)

    def seek(self, timestamp):
        self.seeker.on_seek = True
        self.seeker.seek(timestamp)

    def shuffle(self):
        self.music_list = random.sample(self.music_list, k=len(self.music_list))
        self.current_index = 0

    def change_loop(self):
        if self.loop_state == LoopState.NOT_ON_LOOP:
            self.loop_state = LoopState.LOOP_QUEUE
        elif self.loop_state == LoopState.LOOP_QUEUE:
            self.loop_state = LoopState.LOOP_TRACK
        elif self.loop_state == LoopState.LOOP_TRACK:
            self.loop_state = LoopState.NOT_ON_LOOP

    def set_next_index(self):
        if self.jump:
            self.jump = False
            return

        match self.loop_state:
            case LoopState.NOT_ON_LOOP:
                self.current_index += 1
            case LoopState.LOOP_QUEUE:
                if self.current_index + 1 == len(self.music_list):
                    self.current_index = 0
                else:
                    self.current_index += 1

    def reached_end_of_queue(self):
        return self.current_index == len(self.music_list)

    def get_elapsed(self):
        now = time.time()
        time_paused = now - self.paused_timestamp if self.paused_timestamp else 0
        return int((now - self.elapsed_timestamp) - time_paused)

    def get_queue_pages(self):
        start = self.current_index
        page = int(start / 10)
        last_page = int((len(self.music_list) - 1) / 10)
        return (page, last_page)

    def get_queue_page(self, page, last_page):
        elapsed = self.get_elapsed()

        if self.loop_state == LoopState.NOT_ON_LOOP:
            in_loop = Translator.translate("q_norep") 
        elif self.loop_state == LoopState.LOOP_QUEUE:
            in_loop = Translator.translate("q_qrep") 
        elif self.loop_state == LoopState.LOOP_TRACK:
            in_loop = Translator.translate("q_songrep").format(song=self.music_list[self.current_index]['title']) if self.current_index < len(self.music_list) else Translator.translate("q_next")
        else:
            return # error

        return Helpers.build_q_page(Helpers.build_q_text(self.music_list, elapsed, self.current_index, page), in_loop, page, last_page)
