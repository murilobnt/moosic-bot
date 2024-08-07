import discord
import datetime
import validators
import re

from urllib.parse import urlparse
from youtubesearchpython import Playlist, VideosSearch

from src.utils.enums import MoosicSearchType, MetaType
from src.utils.moosic_error import MoosicError
from src.utils.moosic_grabber import MoosicVideo
from src.utils.helpers import Helpers

class InteractiveText:
    def __init__(self, sent_text, response):
        self.sent_text = sent_text
        self.response = response

class MoosicFinder:
    @staticmethod
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
            elif urlparse(input).netloc == "open.spotify.com":
                path = urlparse(input).path.split("/")[1] 
                match path:
                    case "playlist":
                        return MoosicSearchType.SPOTIFY_ALBUM
                    case "album":
                        return MoosicSearchType.SPOTIFY_ALBUM
                    case "track":
                        return MoosicSearchType.SPOTIFY_SONG
                    case _:
                        return MoosicSearchType.UNKNOWN
            else:
                return MoosicSearchType.UNKNOWN
        else:
            return MoosicSearchType.SEARCH_STRING

    @staticmethod
    def fetch_yt_playlist(url):
        pl = Playlist(url)
        while pl.hasMoreVideos:
            pl.getNextVideos()
        return pl.videos

    @staticmethod
    def gen_spotify_playlist(playlist_items):
        meta_list = []
        for item in playlist_items:
            if item.get('track'):
                meta = { 'type'            : MetaType.SPOTIFY,
                         'title'           : item['track']['name'],
                         'url'             : item['track']['external_urls']['spotify'],
                         'duration'        : int(item['track']['duration_ms'] / 1000),
                         'search_query'    : f"{item['track']['artists'][0]['name']} {item['track']['name']} views"
                       }
            else:
                meta = { 'type'            : MetaType.SPOTIFY,
                         'title'           : item['name'],
                         'url'             : item['external_urls']['spotify'],
                         'duration'        : int(item['duration_ms'] / 1000),
                         'search_query'    : f"{item['artists'][0]['name']} {item['name']} views"
                        } 
            meta_list.append(meta)
        return meta_list

    @staticmethod
    def gen_youtube_playlist(playlist_items):
        meta_list = []
        for item in playlist_items:
            meta = { 'type'     : MetaType.YOUTUBE,
                     'title'    : item.get('title'),
                     'url'      : f"https://youtube.com/watch?v={item.get('id')}",
                     'id'       : item.get('id'),
                     'duration' : Helpers.time_to_seconds(Helpers.str_to_time(item.get('duration')))
                   }
            meta_list.append(meta)
        return meta_list

    @staticmethod
    def gen_youtube_song_search(song_info):
        duration = Helpers.time_to_seconds(Helpers.str_to_time(song_info.get('duration'))) if song_info.get('duration') else None

        meta = { 'type'     : MetaType.YOUTUBE,
                 'title'    : song_info.get('title'),
                 'url'      : f"https://youtube.com/watch?v={song_info.get('id')}",
                 'id'       : song_info.get('id'),
                 'duration' : duration
                }
        return meta

    @staticmethod
    def gen_youtube_song_url(info : MoosicVideo):
        meta = { 'type'     : MetaType.YOUTUBE,
                 'title'    : info.get_title(),
                 'url'      : f"https://youtube.com/watch?v={info.get_id()}",
                 'id'       : info.get_id(),
                 'duration' : info.get_duration()
                }
        return meta

    @staticmethod
    def gen_spotify_song(song_info):
        meta = { 'type'            : MetaType.SPOTIFY,
                 'title'           : song_info['name'],
                 'url'             : song_info['external_urls']['spotify'],
                 'duration'        : int(song_info['duration_ms'] / 1000),
                 'search_query'    : f"{song_info['artists'][0]['name']} {song_info['name']} views"
               }
        return meta

    @staticmethod
    async def send_added_song_message(position, title, url, text_channel, author_mention):
        # description = translator.translate("song_add", ctx.guild.id).format(index=position, title=title, url=url, mention=author_mention)
        description = f"Adicionou música {title} na posição {position} (vou mudar depois)"
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        await text_channel.send(embed=embed)

    @staticmethod
    async def send_added_playlist_message(pl_length, text_channel, author_mention):
        # description = translator.translate("pl_add", ctx.guild.id).format(pl_len=pl_length, mention=author_mention)
        description = f"Adicionou playlist com {pl_length} (vou mudar depois)"
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        await text_channel.send(embed=embed)

    @staticmethod
    def search_youtube(query):
        try:
            return VideosSearch(query, limit=10).result().get("result")
        except:
            raise MoosicError("er_url") #er_url
