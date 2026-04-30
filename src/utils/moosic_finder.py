import discord
import datetime
import validators
import re
import requests

from urllib.parse import urlparse
from youtube_search import YoutubeSearch
from pytubefix import Playlist

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
            if re.match(r"(m\.|www\.)?(youtu\.be|youtube\.com)", parsed_url.netloc):
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
                        return MoosicSearchType.SPOTIFY_PLAYLIST
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
    def extract_video_information(video_entry):
        return {'title': video_entry['playlistVideoRenderer']['title']['runs'][0]['text'], 'id': video_entry['playlistVideoRenderer']['videoId'], 'duration': str(video_entry['playlistVideoRenderer']['lengthSeconds'])}

    @staticmethod
    def get_remaining_videos(token):
        continue_token = token
        added_videos = []

        retries = 3
        timeout = 10

        yt_api_url = 'https://www.youtube.com/youtubei/v1/browse'
        headers = { 'Content-Type' : 'application/json' }
        request_data = {
            'context': {
                'client': {
                    'clientName': 'WEB',
                    'clientVersion': '2.20240313.05.00'
                }
            }
        }

        # FOR MY FUTURE SELF: THIS IS A DO-WHILE
        while True:
            request_data['continuation'] = continue_token

            attempts = 1

            while True:
                response = requests.post(yt_api_url, headers=headers, json=request_data, timeout=10)
                got_data = response.json()
                continuation_videos = got_data['onResponseReceivedActions'][0]['appendContinuationItemsAction']['continuationItems']

                if 'lockupViewModel' in continuation_videos[-1]:
                    if attempts == 4:
                        raise MoosicError("er_url")
                    attempts += 1
                else:
                    break

            for video in continuation_videos:
                try:
                    added_videos.append(MoosicFinder.extract_video_information(video))
                except KeyError:
                    continue

            if 'continuationItemRenderer' in continuation_videos[-1]:
                continue_token = continuation_videos[-1]['continuationItemRenderer']['continuationEndpoint']['continuationCommand']['token']
            else:
                break

        return added_videos

    @staticmethod
    def fetch_yt_playlist(url):
        pl = Playlist(url)

        attempts = 1
        while True:
            try:
                playlist_videos = pl.initial_data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer']['contents']
                break
            except KeyError:
                if attempts == 4:
                    raise MoosicError("er_url")
                attempts += 1
        videos = []

        for video in playlist_videos:
            try:
                videos.append(MoosicFinder.extract_video_information(video))
            except KeyError:
                continue

        if "continuationItemRenderer" in playlist_videos[-1]:
            continue_token = playlist_videos[-1]['continuationItemRenderer']['continuationEndpoint']['commandExecutorCommand']['commands'][1]['continuationCommand']['token']
            videos.extend(MoosicFinder.get_remaining_videos(continue_token))

        return videos

    @staticmethod
    def gen_spotify_album(album_items):
        meta_list = []
        for item in album_items:
            meta = { 'type'            : MetaType.SPOTIFY,
                     'title'           : item['name'],
                     'url'             : item['external_urls']['spotify'],
                     'duration'        : int(item['duration_ms'] / 1000),
                     'search_query'    : f"{item['artists'][0]['name']} {item['name']}"
                    } 
            meta_list.append(meta)
        return meta_list

    @staticmethod
    def gen_spotify_playlist(playlist_items):
        meta_list = []
        for item in playlist_items:
            meta = { 'type'            : MetaType.SPOTIFY,
                     'title'           : item['title'],
                     'url'             : f"https://open.spotify.com/track/{item['uri'].split(":")[-1]}",
                     'duration'        : int(item['duration'] / 1000),
                     'search_query'    : f"{item['subtitle']} {item['title']}"
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
                     'duration' : int(item.get('duration'))
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
                 'search_query'    : f"{song_info['artists'][0]['name']} {song_info['name']}"
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
        return YoutubeSearch(query, max_results=10).videos
        #sorted_lookup = sorted(lookup, key=lambda x: int(x['views'].split(" ")[0].replace(".", "")), reverse=True)
        #return sorted_lookup
