import spotipy
import validators
import re
import asyncio

from enum import Enum
from urllib.parse import urlparse, parse_qs
from youtubesearchpython.__future__ import Video, Playlist, VideosSearch, StreamURLFetcher
from spotipy.oauth2 import SpotifyClientCredentials

from src.utils.helpers import time_to_seconds, str_to_time

class MoosicSearchType(Enum):
    SEARCH_STRING = 1
    YOUTUBE_SONG = 2
    YOUTUBE_SHORTS = 3
    YOUTUBE_PLAYLIST = 4
    SPOTIFY_SONG = 5
    SPOTIFY_ALBUM = 6
    UNKNOWN = 7

class InteractiveText:
    def __init__(self, sent_text, response):
        self.sent_text = sent_text
        self.response = response

def build_choose_text(entries):
    songs_str = ""
    i = 1
    for entry in entries:
        songs_str = songs_str + "[" + str(i) + f"] : {entry.get('title')} <por {entry.get('channel').get('name')}, {entry.get('duration')}>"
        if not i == len(entries):
            songs_str = songs_str + "\n"
        i += 1

    return songs_str

def get_input_type(input) -> MoosicSearchType:
    if validators.url(input):
        # url handling
        parsed_url = urlparse(input)
        if re.match("(m\.|www\.)?(youtu\.be|youtube\.com)", parsed_url.netloc):
            path = parsed_url.path.split("/")[1] 
            match path:
                case "playlist":
                    return MoosicSearchType.YOUTUBE_PLAYLIST
                case "shorts":
                    return MoosicSearchType.YOUTUBE_SHORTS
                case _:
                    return MoosicSearchType.YOUTUBE_SONG
        elif urlparse(url).netloc == "open.spotify.com":
            path = urlparse(url).path.split("/")[1] 
            match path:
                case "playlist":
                    return MoosicSearchType.SPOTIFY_ALBUM
                match "track":
                    return MoosicSearchType.SPOTIFY_SONG
                match _:
                    return MoosicSearchType.UNKNOWN
        else:
            return MoosicSearchType.UNKNOWN
    else:
        return MoosicSearchType.SEARCH_STRING

async def fetch_yt_playlist(url):
    pl = Playlist(url)
    while pl.hasMoreVideos:
        await pl.getNextVideos()
    return pl.videos

def gen_spotify_playlist(playlist_items):
    meta_list = []
    for item in playlist_items:
        meta = { 'type'            : MetaType.SPOTIFY,
                 'title'           : item['track']['name'],
                 'url'             : item['track']['external_urls']['spotify'],
                 'duration'        : int(item['track']['duration_ms'] / 1000),
                 'search_query'    : f"{item['track']['artists'][0]['name']} {item['track']['name']} views"
               }
        meta_list.append(meta)
    return meta_list

def gen_youtube_playlist(playlist_items):
    meta_list = []
    for item in playlist_items:
        meta = { 'type'     : MetaType.YOUTUBE,
                 'title'    : item.get('title'),
                 'url'      : f"https://youtube.com/watch?v={item.get('id')}",
                 'id'       : item.get('id'),
                 'duration' : time_to_seconds(str_to_time(item.get('duration')))
               }
        meta_list.append(meta)
    return meta_list

def gen_youtube_song(song_info):
    if song_info.get('type'):
        # Through search
        duration = time_to_seconds(str_to_time(info.get('duration'))) if info.get('duration') else None
    else:
        # Through URL
        duration = int(info.get('duration')['secondsText']) if not info.get('isLiveContent') else None

    meta = { 'type'     : MetaType.YOUTUBE,
             'title'    : song_info.get('title'),
             'url'      : f"https://youtube.com/watch?v={song_info.get('id')}",
             'id'       : song_info.get('id'),
             'duration' : duration
            }
    return meta

def gen_spotify_song(song_info):
    meta = { 'type'            : MetaType.SPOTIFY,
             'title'           : song_info['name'],
             'url'             : song_info['external_urls']['spotify'],
             'duration'        : int(song_info['duration_ms'] / 1000),
             'search_query'    : f"{song_info['artists'][0]['name']} {song_info['name']} views"
           }
    return meta

async def input_to_meta(input, guild_meta_list, sp, send_and_choose):
    input_type = get_input_type(input)
    parsed_url = urlparse(input) if validators.url(input) else None

    match input_type:
        case MoosicSearchType.YOUTUBE_SONG:
            try:
                vd = await Video.get(input)
                guild_meta_list.append(vd)
            except:
                raise MoosicError("er_himalformed") #er_himalformed
        case MoosicSearchType.YOUTUBE_SHORTS:
            try:
                video_id = parsed_url.path.split("/")[2]
                vd = await Video.get(video_id)
                guild_meta_list.append(vd)
            except:
                raise MoosicError("er_himalformed") #er_himalformed
            pass
        case MoosicSearchType.YOUTUBE_PLAYLIST:
            pl = fetch_yt_playlist(input)
            guild_meta_list.extend(pl)
        case MoosicSearchType.SPOTIFY_SONG:
            track_URI = url.split("/")[-1].split("?")[0]
            track = sp.track(track_URI)
            guild_meta_list.append(gen_spotify_song(track))
        case MoosicSearchType.SPOTIFY_ALBUM:
            playlist_URI = url.split("/")[-1].split("?")[0]
            tracks_uri = sp.playlist_tracks(playlist_URI)["items"]
            guild_meta_list.append(gen_spotify_playlist(tracks_uri))
        case MoosicSearchType.SEARCH_STRING:
            try:
                entries = (await VideosSearch(url, limit=10).next()).get("result")
                interactive_text = await send_and_choose(build_choose_text(entries))
                choice = int(interactive_text.response.content)
                if choice < 1 or choice > len(entries):
                    raise MoosicError("er_shoutlen") #er_shoutlen
                    await interactive_text.sent_text.delete()
                info = entries[choice - 1]
                await interactive_text.sent_text.delete()
            except:
                raise MoosicError("er_url") #er_url
        case _:
            raise MoosicError("er_himalformed") #er_himalformed or unknown

    return input_type
