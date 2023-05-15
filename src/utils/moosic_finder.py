import discord
import datetime
import validators
import re

from urllib.parse import urlparse, parse_qs
from youtubesearchpython.__future__ import Video, Playlist, VideosSearch

from src.utils.enums import MoosicSearchType, MetaType
from src.utils.moosic_error import MoosicError

class InteractiveText:
    def __init__(self, sent_text, response):
        self.sent_text = sent_text
        self.response = response

class MoosicFinder:
    @staticmethod
    def time_to_seconds(time):
        return (time.hour * 60 + time.minute) * 60 + time.second

    @staticmethod
    def str_to_time(time_str):
        time_match = re.match('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$', time_str)
        if time_match.group(1):
            FORMAT = "%H:%M:%S"
        elif time_match.group(2):
            FORMAT = "%M:%S"
        elif time_match.group(3):
            FORMAT = "%S"
        return datetime.datetime.strptime(time_str, FORMAT).time()

    @staticmethod
    def build_choose_text(entries):
        songs_str = ""
        i = 1
        for entry in entries:
            songs_str = songs_str + "[" + str(i) + f"] : {entry.get('title')} <{entry.get('channel').get('name')}, {entry.get('duration')}>"
            if not i == len(entries):
                songs_str = songs_str + "\n"
            i += 1

        return songs_str

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
    async def fetch_yt_playlist(url):
        pl = Playlist(url)
        while pl.hasMoreVideos:
            await pl.getNextVideos()
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
                     'duration' : MoosicFinder.time_to_seconds(MoosicFinder.str_to_time(item.get('duration')))
                   }
            meta_list.append(meta)
        return meta_list

    @staticmethod
    def gen_youtube_song(song_info):
        if song_info.get('type'):
            # Through search
            duration = MoosicFinder.time_to_seconds(MoosicFinder.str_to_time(song_info.get('duration'))) if song_info.get('duration') else None
        else:
            # Through URL
            duration = int(song_info.get('duration')['secondsText']) if not song_info.get('isLiveContent') else None

        meta = { 'type'     : MetaType.YOUTUBE,
                 'title'    : song_info.get('title'),
                 'url'      : f"https://youtube.com/watch?v={song_info.get('id')}",
                 'id'       : song_info.get('id'),
                 'duration' : duration
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
    async def send_added_message(queue, description):
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        await queue.get('text_channel').send(embed=embed)

    @staticmethod
    async def add_song_or_playlist(input, queue, sp, ctx, translator, send_and_choose):
        input_type = MoosicFinder.get_input_type(input)
        parsed_url = urlparse(input) if validators.url(input) else None
        playlist = False

        match input_type:
            case MoosicSearchType.YOUTUBE_SONG:
                try:
                    vd = await Video.get(input, get_upload_date=True)
                    queue.get('meta_list').append(MoosicFinder.gen_youtube_song(vd))
                except:
                    raise MoosicError("er_himalformed") #er_himalformed
            case MoosicSearchType.YOUTUBE_SHORTS:
                try:
                    video_id = parsed_url.path.split("/")[2]
                    vd = await Video.get(video_id, get_upload_date=True)
                    queue.get('meta_list').append(MoosicFinder.gen_youtube_song(vd))
                except:
                    raise MoosicError("er_himalformed") #er_himalformed
                pass
            case MoosicSearchType.YOUTUBE_PLAYLIST:
                fetch_pl = await MoosicFinder.fetch_yt_playlist(input)
                pl = MoosicFinder.gen_youtube_playlist(fetch_pl)
                queue.get('meta_list').extend(pl)
                pl_len = len(pl)
                playlist = True
            case MoosicSearchType.SPOTIFY_SONG:
                track_URI = input.split("/")[-1].split("?")[0]
                track = sp.track(track_URI)
                queue.get('meta_list').append(MoosicFinder.gen_spotify_song(track))
            case MoosicSearchType.SPOTIFY_ALBUM:
                playlist_URI = input.split("/")[-1].split("?")[0]
                try:
                    tracks_uri = sp.playlist_tracks(playlist_URI)["items"]
                except:
                    tracks_uri = sp.album_tracks(playlist_URI)["items"]
                pl = MoosicFinder.gen_spotify_playlist(tracks_uri)
                queue.get('meta_list').extend(pl)
                pl_len = len(pl)
                playlist = True
            case MoosicSearchType.SEARCH_STRING:
                try:
                    entries = (await VideosSearch(input, limit=10).next()).get("result")
                except:
                    raise MoosicError("er_url") #er_url

                interactive_text = await send_and_choose(MoosicFinder.build_choose_text(entries))
                try:
                    choice = int(interactive_text.response.content)
                except ValueError:
                    await interactive_text.sent_text.delete()
                    raise MoosicError("play_shcancel")
                if choice < 1 or choice > len(entries):
                    await interactive_text.sent_text.delete()
                    raise MoosicError("er_shoutlen") #er_shoutlen
                info = entries[choice - 1]
                await interactive_text.sent_text.delete()
                queue.get('meta_list').append(MoosicFinder.gen_youtube_song(info))
            case _:
                raise MoosicError("er_himalformed") #er_himalformed or UNKNOWN

        if playlist:
            description = translator.translate("pl_add", ctx.guild.id).format(pl_len=pl_len, mention=ctx.author.mention)
            await MoosicFinder.send_added_message(queue, description)
        else:
            cur_song = queue.get('meta_list')[-1]
            description = translator.translate("song_add", ctx.guild.id).format(index=len(queue.get('meta_list')), title=cur_song.get('title'), url=cur_song.get('url'), mention=ctx.author.mention)
            await MoosicFinder.send_added_message(queue, description)

    # Deprecated
    @staticmethod
    async def input_to_meta(input, guild_meta_list, sp, send_and_choose):
        input_type = MoosicFinder.get_input_type(input)
        parsed_url = urlparse(input) if validators.url(input) else None

        match input_type:
            case MoosicSearchType.YOUTUBE_SONG:
                try:
                    vd = await Video.get(input)
                    guild_meta_list.append(MoosicFinder.gen_youtube_song(vd))
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
                pl = await MoosicFinder.fetch_yt_playlist(input)
                guild_meta_list.extend(pl)
            case MoosicSearchType.SPOTIFY_SONG:
                track_URI = input.split("/")[-1].split("?")[0]
                track = sp.track(track_URI)
                guild_meta_list.append(MoosicFinder.gen_spotify_song(track))
            case MoosicSearchType.SPOTIFY_ALBUM:
                playlist_URI = input.split("/")[-1].split("?")[0]
                tracks_uri = sp.playlist_tracks(playlist_URI)["items"]
                guild_meta_list.append(MoosicFinder.gen_spotify_playlist(tracks_uri))
            case MoosicSearchType.SEARCH_STRING:
                try:
                    entries = (await VideosSearch(input, limit=10).next()).get("result")
                except:
                    raise MoosicError("er_url") #er_url

                interactive_text = await send_and_choose(MoosicFinder.build_choose_text(entries))
                try:
                    choice = int(interactive_text.response.content)
                except ValueError:
                    await interactive_text.sent_text.delete()
                    raise MoosicError("play_shcancel")
                if choice < 1 or choice > len(entries):
                    await interactive_text.sent_text.delete()
                    raise MoosicError("er_shoutlen") #er_shoutlen
                info = entries[choice - 1]
                await interactive_text.sent_text.delete()
                guild_meta_list.append(MoosicFinder.gen_youtube_song(info))
            case _:
                raise MoosicError("er_himalformed") #er_himalformed or unknown

        return input_type
