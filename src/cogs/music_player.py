import discord
import spotipy
import asyncio
import random
import time
import re
import validators
import traceback
import os

import datetime
from spotipy.oauth2 import SpotifyClientCredentials
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands
from youtubesearchpython.__future__ import Video, Playlist, VideosSearch, StreamURLFetcher

from enum import Enum
from functools import partial
from urllib.parse import urlparse, parse_qs

from src.utils.music_verifications import MusicVerifications
from src.utils.moosic_error import MoosicError
from src.database.async_database import create_get_guild_record
from src.language.translator import Translator

class Filter:
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class LoopState(Enum):
    NOT_ON_LOOP = 1
    LOOP_QUEUE = 2
    LOOP_TRACK = 3

class MetaType(Enum):
    YOUTUBE = 1
    SPOTIFY = 2

class MusicPlayer(commands.Cog):
    """desc_mp"""
    def __init__(self, bot, servers_settings):
        self.bot = bot
        self.servers_queues = {}
        self.translator = Translator(servers_settings)
        self.verificator = MusicVerifications(self.translator, self.servers_queues)
        self.sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=os.environ["SP_CLIENT"], client_secret=os.environ["SP_SECRET"]))
        self.fetcher = StreamURLFetcher()
        self.fetcher._getJS()

    async def play_song_index(self, ctx, queue, song_index):
        modifier = 2 if not queue.get('halt_task') and not queue.get('loop') == LoopState.LOOP_TRACK else 1
        url_int = song_index - modifier

        if url_int < 1 - modifier or url_int > len(queue['meta_list']) - modifier:
            raise MoosicError(self.translator.translate("er_index", ctx.guild.id))

        queue['song_index'] = url_int

    def spotify_playlist(self, tracks_uri):
        meta_list = []
        for item in tracks_uri:
            meta = { 'type'            : MetaType.SPOTIFY,
                     'title'           : item['track']['name'],
                     'url'             : item['track']['external_urls']['spotify'],
                     'duration'        : int(item['track']['duration_ms'] / 1000),
                     'search_query'    : f"{item['track']['artists'][0]['name']} {item['track']['name']} spotify"
                   }
            meta_list.append(meta)
        return meta_list

    def youtube_playlist(self, playlist_items):
        meta_list = []
        for item in playlist_items:
            meta = { 'type'     : MetaType.YOUTUBE,
                     'title'    : item.get('title'),
                     'url'      : f"https://youtube.com/watch?v={item.get('id')}",
                     'id'       : item.get('id'),
                     'duration' : self.time_to_seconds(self.str_to_time(item.get('duration')))
                   }
            meta_list.append(meta)
        return meta_list

    async def handle_input(self, guild_id, queue, url, author, created_queue, text_channel):
        if validators.url(url):
            # url handling
            parsed_url = urlparse(url)
            if re.match("(m\.|www\.)?(youtu\.be|youtube\.com)", parsed_url.netloc):
                if parsed_url.path.split("/")[1] == "playlist":
                    pl = Playlist(url)
                    while pl.hasMoreVideos:
                        await pl.getNextVideos()
                    await self.enqueue_playlist(guild_id, text_channel, queue, self.youtube_playlist(pl.videos), author.mention)
                else:
                    try:
                        vd = await Video.get(url)
                    except:
                        raise MoosicError(self.translator.translate("er_himalformed", guild_id))
                    await self.enqueue_yt_song(guild_id, text_channel, queue, vd, author.mention)
            elif urlparse(url).netloc == "open.spotify.com":
                if urlparse(url).path.split("/")[1] == "playlist":
                    playlist_URI = url.split("/")[-1].split("?")[0]
                    tracks_uri = self.sp.playlist_tracks(playlist_URI)["items"]
                    await self.enqueue_playlist(guild_id, text_channel, queue, self.spotify_playlist(tracks_uri), author.mention)
                elif urlparse(url).path.split("/")[1] == "track":
                    track_URI = url.split("/")[-1].split("?")[0]
                    track = self.sp.track(track_URI)
                    await self.enqueue_sp_song(guild_id, text_channel, queue, track, author.mention)
                else:
                    raise MoosicError(self.translator.translate("er_hispotifyuri", guild_id))
                return
            else:
                raise MoosicError(self.translator.translate("er_hidomain", guild_id))
        else:
            # search handling
            try:
                entries = (await VideosSearch(url, limit=5).next()).get("result")
            except Exception:
                print(traceback.format_exc())
                if created_queue:
                    self.ensure_queue_deleted(ctx.guild.id)
                raise MoosicError(self.translator.translate("er_url", guild_id))

            trans_words = {'by' : self.translator.translate("play_by", guild_id)}
            choice_picker = await text_channel.send(self.translator.translate("play_buildt", guild_id).format(songs_str=self.build_choose_text(entries, trans_words)))
            try:
                response = await self.bot.wait_for('message', timeout=30, check=lambda message: message.author == author and message.channel == text_channel)
            except asyncio.TimeoutError:
                await choice_picker.delete()
                raise MoosicError(self.translator.translate("er_shtimeout", guild_id))
            try:
                choice = int(response.content)
                if choice < 1 or choice > len(entries):
                    await choice_picker.delete()
                    raise MoosicError(self.translator.translate("er_shoutlen", guild_id))
                info = entries[choice - 1]
                await choice_picker.delete()
            except ValueError:
                await choice_picker.delete()
                msg = await text_channel.send(self.translator.translate("play_shcancel", guild_id))
                await msg.delete(delay=10)
                return 1
                
            self.verificator.verify_info_fields(info)
            await self.enqueue_yt_song(guild_id, text_channel, queue, info, author.mention)

    def format_duration(self, duration):
        if not duration:
            return "LIVE"
        if duration >= 3600:
            return time.strftime("%H:%M:%S", time.gmtime(int(duration)))
        else:
            return time.strftime("%M:%S", time.gmtime(int(duration)))

    def build_choose_text(self, entries, trans_words):
        songs_str = ""
        i = 1
        for entry in entries:
            songs_str = songs_str + "[" + str(i) + f"] : {entry.get('title')} <{trans_words.get('by')} {entry.get('channel').get('name')}, {entry.get('duration')}>"
            if not i == len(entries):
                songs_str = songs_str + "\n"
            i += 1

        return songs_str

    async def connect_and_play(self, ctx, queue):
        try:
            queue['connection'] = await ctx.author.voice.channel.connect()
            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
            await self.play_songs(ctx.guild.id)
        except (asyncio.TimeoutError, discord.ClientException) as e:
            self.ensure_queue_deleted(ctx.guild.id)
            raise MoosicError(self.translator.translate("er_conc", ctx.guild.id))

    def cancel_halt_task(self, queue):
        if queue.get('halt_task'):
            if not queue['halt_task'].done():
                queue['halt_task'].cancel()

            queue['halt_task'] = None

    def cancel_alone_task(self, queue):
        if queue.get('alone_task'):
            if not queue['alone_task'].done():
                queue['alone_task'].cancel()

            queue['alone_task'] = None

    @commands.command(aliases=['p', 't', 'tocar'], description="ldesc_play", pass_context=True)
    async def play(self, ctx, *, url : str):
        """Toca uma música, ou um índice de música na fila, e conecta o bot a um canal de voz"""
        self.verificator.verify_user_voice(ctx)

        channel_permissions = ctx.author.voice.channel.permissions_for(ctx.guild.me)
        if not channel_permissions.connect or not channel_permissions.speak:
            raise MoosicError(self.translator.translate("er_perm", ctx.guild.id))

        queue = self.servers_queues.get(ctx.guild.id)
        created_queue = False

        if queue and queue.get('connection') and ctx.author.voice and ctx.voice_client and ctx.author.voice.channel != ctx.voice_client.channel:
            connection = queue['connection']
            connection.stop()
            await connection.disconnect()
            self.ensure_queue_deleted(ctx.guild.id)

        if not queue:
            created_queue = True
            queue = self.create_queue(ctx.guild.id, ctx.message.channel)

        song_index = None
        try:
            song_index = int(url)
        except ValueError:
            pass
        
        try:
            if song_index:
                self.verificator.verify_connection(ctx, queue)
                self.verificator.verify_no_songs(ctx, queue)
                await self.play_song_index(ctx, queue, song_index)
                if not queue.get('halt_task'):
                    queue['connection'].stop()
            else:
                result = await self.handle_input(ctx.guild.id, queue, url, ctx.author, created_queue, ctx.message.channel)
                if result:
                    if created_queue:
                        self.servers_queues.pop(ctx.guild.id)
                    return
        except:
            if created_queue:
                self.servers_queues.pop(ctx.guild.id)
            raise

        if created_queue:
            await self.connect_and_play(ctx, queue)
        elif queue.get('halt_task'):
            self.cancel_halt_task(queue)
            await self.play_songs(ctx.guild.id)

    def create_queue(self, guild_id, text_channel):
        queue = {
                'text_channel'        : text_channel,
                'connection'          : None,
                'meta_list'           : [],
                'song_index'          : 0,
                'now_playing_message' : None,
                'same_song'           : None,
                'elapsed_time'        : None,
                'paused_time'         : None,
                'halt_task'           : None,
                'alone_task'          : None,
                'current_audio_url'   : None,
                'loop'                : LoopState.NOT_ON_LOOP
                 }

        self.servers_queues[guild_id] = queue
        return queue

    def str_to_time(self, time_str):
        time_match = re.match('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$', time_str)
        if time_match.group(1):
            FORMAT = "%H:%M:%S"
        elif time_match.group(2):
            FORMAT = "%M:%S"
        elif time_match.group(3):
            FORMAT = "%S"
        return datetime.datetime.strptime(time_str, FORMAT).time()

    def time_to_seconds(self, _time):
        return (_time.hour * 60 + _time.minute) * 60 + _time.second

    async def enqueue_yt_song(self, guild_id, text_channel, queue, info, mention):
        if info.get('type'):
            # Through search
            duration = self.time_to_seconds(self.str_to_time(info.get('duration'))) if info.get('duration') else None
        else:
            # Through URL
            duration = int(info.get('duration')['secondsText']) if not info.get('isLiveContent') else None

        meta = { 'type'     : MetaType.YOUTUBE,
                 'title'    : info.get('title'),
                 'url'      : f"https://youtube.com/watch?v={info.get('id')}",
                 'id'       : info.get('id'),
                 'duration' : duration
                }
        queue['meta_list'].append(meta)

        description = self.translator.translate("song_add", guild_id).format(index=len(queue.get('meta_list')), title=meta.get('title'), url=meta.get('url'), mention=mention)
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        queue['text_channel'] = text_channel
        await text_channel.send(embed=embed)
    
    async def enqueue_sp_song(self, guild_id, text_channel, queue, info, mention):
        meta = { 'type'            : MetaType.SPOTIFY,
                 'title'           : info['name'],
                 'url'             : info['external_urls']['spotify'],
                 'duration'        : int(info['duration_ms'] / 1000),
                 'search_query'    : f"{info['artists'][0]['name']} {info['name']} spotify"
               }
        queue['meta_list'].append(meta)

        description = self.translator.translate("song_add", guild_id).format(index=len(queue.get('meta_list')), title=meta.get('title'), url=meta.get('url'), mention=mention)
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        queue['text_channel'] = text_channel
        await text_channel.send(embed=embed)
    
    async def enqueue_playlist(self, guild_id, text_channel, queue, playlist, mention):
        queue['meta_list'].extend(playlist)

        description = self.translator.translate("pl_add", guild_id).format(pl_len=len(playlist), mention=mention)
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        queue['text_channel'] = text_channel
        await text_channel.send(embed=embed)

    @commands.command(aliases=['pular'], description="ldesc_skip", pass_context=True) 
    async def skip(self, ctx, *, how_many : int = None):
        """Pula um determinado número de músicas na fila"""
        self.verificator.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        self.verificator.verify_is_playing(queue)
        if how_many:
            try:
                how_many = int(how_many)
                if how_many <= 0:
                    raise MoosicError(self.translator.translate("er_skipindex", ctx.guild.id))
            except ValueError:
                raise MoosicError(self.translator.translate("er_skiparg", ctx.guild.id))
        else:
            how_many = 1

        if how_many > len(queue['meta_list']) - queue['song_index']:
            how_many = len(queue['meta_list']) - queue['song_index']

        queue['song_index'] += how_many if queue['loop'] == LoopState.LOOP_TRACK else how_many - 1

        description = self.translator.translate("skip_succ", ctx.guild.id).format(how_many=how_many)
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        asyncio.create_task(ctx.send(embed=embed))

        queue['connection'].stop()

    @commands.command(aliases=['pausar'], description="ldesc_pause", pass_context=True)
    async def pause(self, ctx):
        """Pausa a música que está tocando"""
        self.verificator.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        self.verificator.verify_is_playing(queue)

        if queue.get('paused_time'):
            raise MoosicError(self.translator.translate("er_paused", ctx.guild.id))

        queue['paused_time'] = time.time()
        queue['connection'].pause()
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=['resumir', 'retomar'], description="ldesc_resume", pass_context=True)
    async def resume(self, ctx):
        """Resume a música que estava tocando"""
        self.verificator.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        self.verificator.verify_is_playing(queue)

        if not queue.get('paused_time'):
            raise MoosicError(self.translator.translate("er_nopause", ctx.guild.id))

        queue['elapsed_time'] = queue['elapsed_time'] + (time.time() - queue['paused_time'])
        queue['paused_time'] = None

        queue['connection'].resume()
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=['aleatorio, random'], description="ldesc_shuffle", pass_context=True)
    async def shuffle(self, ctx):
        self.verificator.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        queue['meta_list'] = random.sample(queue.get('meta_list'), k=len(queue.get('meta_list')))
        queue['song_index'] = -1
        queue['connection'].stop()

        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=['time', 'to', 'para', 'em', 'tempo'], description="ldesc_seek", pass_context=True)
    async def seek(self, ctx, timestamp : str):
        """Vai para um determinado tempo da música"""
        self.verificator.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)

        if not re.match('^(\d{1,2}:)?(\d{1,2}:)?(\d{1,2})$', timestamp) and not re.match('^\d+$', timestamp):
            raise MoosicError(self.translator.translate("er_seekarg", ctx.guild.id))

        failed1 = False
        failed2 = False

        try:
            m_time = time.strptime(timestamp, "%M:%S")
            gap = datetime.timedelta(minutes=m_time.tm_min, seconds=m_time.tm_sec).seconds
        except:
            print(traceback.format_exc())
            failed1 = True

        try:
            m_time = time.strptime(timestamp, "%H:%M:%S")
            gap = datetime.timedelta(hours=m_time.tm_hour, minutes=m_time.tm_min, seconds=m_time.tm_sec).seconds
        except:
            failed2 = True
        
        if failed1 and failed2:
            try:
                gap = int(timestamp)
            except ValueError:
                raise MoosicError(self.translator.translate("er_seekarg", ctx.guild.id))

        queue['same_song'] = {'gap': gap, 'before_options': f"-ss {timestamp}"} 
        queue['connection'].stop()
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=['now_playing', 'tocando_agora', 'ta'], description="ldesc_np", pass_context=True)
    async def np(self, ctx):
        """Disponibiliza informações da música que está tocando"""
        self.verificator.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        self.verificator.verify_is_playing(queue)

        if not queue['elapsed_time']:
            raise MoosicError(self.translator.translate("er_npdat", ctx.guild.id))

        now = time.time()
        song = queue['meta_list'][queue['song_index']]
        time_paused = now - queue['paused_time'] if queue['paused_time'] else 0
        elapsed = int((now - queue['elapsed_time']) - time_paused)
        duration = song.get('duration')
            
        if elapsed < 60:
            formatted_elapsed = (time.strftime("%-Ss", time.gmtime(elapsed)))
        elif elapsed < 3600:
            formatted_elapsed = (time.strftime("%-Mm %-Ss", time.gmtime(elapsed)))
        else:
            formatted_elapsed = (time.strftime("%-Hh %-Mm %-Ss", time.gmtime(elapsed)))

        if duration < 60:
            formatted_duration = (time.strftime("%-Ss", time.gmtime(duration)))
        elif duration < 3600:
            formatted_duration = (time.strftime("%-Mm %-Ss", time.gmtime(duration)))
        else:
            formatted_duration = (time.strftime("%-Hh %-Mm %-Ss", time.gmtime(duration)))

        if not song.get("duration_str") == "0":
            completion_bar = int((elapsed/duration) * 20)
            complement_bar = 20 - completion_bar

            progress_bar = '' + "▮"*completion_bar + "▯"*complement_bar
            description = self.translator.translate("np_succnorm", ctx.guild.id).format(index=queue['song_index']+1, title=song.get('title'), weburl=song.get('url'), mention=ctx.author.mention, progress_bar=progress_bar, formatted_elapsed=formatted_elapsed, formatted_duration=formatted_duration)
            embed = discord.Embed(
                    description=description,
                    color=0xedd400)
            await ctx.send(embed=embed)
        else:
            description = self.translator.translate("np_succlive", ctx.guild.id).format(index=queue['song_index']+1, title=song.get('title'), weburl=song.get('url'), mention=ctx.author.mention, formatted_elapsed=formatted_elapsed)
            embed = discord.Embed(
                    description=description,
                    color=0xedd400)
            await ctx.send(embed=embed)

    @commands.command(aliases=['q', 'fila', 'f', 'cola', 'c'], description="ldesc_queue", pass_context=True)
    async def queue(self, ctx, song_index : int = None):
        """Mostra informações da lista de músicas"""
        self.verificator.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)

        meta_list = queue['meta_list'][:]
        start = 0 if not song_index else min(len(meta_list), song_index)
        page = int((start - 1) / 10)
        last_page = int((len(meta_list) - 1) / 10)

        now = time.time()
        time_paused = now - queue['paused_time'] if queue['paused_time'] else 0
        elapsed = int((now - queue['elapsed_time']) - time_paused) if queue['elapsed_time'] else 0
        song_index = queue['song_index']

        il_index = "q_norep" if queue['loop'] == LoopState.NOT_ON_LOOP else "q_qrep" if queue['loop'] == LoopState.LOOP_QUEUE else "q_songrep" if queue['loop'] == LoopState.LOOP_TRACK else ":P"
        in_loop = ""

        if il_index == "q_songrep":
            in_loop = self.translator.translate(il_index, ctx.guild.id).format(song=queue['meta_list'][queue['song_index']]['title']) if queue['song_index'] < len(queue['meta_list']) else self.translator.translate("q_next", ctx.guild.id)
        elif il_index == ":P":
            in_loop = ":P"
        else:
            in_loop = self.translator.translate(il_index, ctx.guild.id) 

        msg = await ctx.send(self.build_page(ctx.guild.id, self.build_text(ctx.guild.id, meta_list, elapsed, song_index, page), in_loop, page, last_page))
        if last_page > 0:
            await msg.add_reaction("◀️")
            await msg.add_reaction("▶️")

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == "▶️":
                    page += 1
                    if page > last_page:
                        page = 0

                    await msg.edit(content=self.build_page(ctx.guild.id, self.build_text(ctx.guild.id, meta_list, elapsed, song_index, page), in_loop, page, last_page))
                    await msg.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "◀️":
                    page -= 1
                    if page < 0:
                        page = last_page
                    await msg.edit(content=self.build_page(ctx.guild.id, self.build_text(ctx.guild.id, meta_list, elapsed, song_index, page), in_loop, page, last_page))
                    await msg.remove_reaction(reaction, user)
                else:
                    await msg.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                break

    def build_text(self, guild_id, meta_list, elapsed, song_index, page):
        songs = ""
        it = 1 + (page * 10)
        index = it

        for entry in meta_list[index - 1 : (index - 1) + 10]:
            live = True if not entry.get('duration') else False

            if not live:
                duration = entry.get('duration')
                if it == song_index + 1 and page == 0:
                    duration = duration - elapsed

                if duration >= 3600:
                    formatted_duration = time.strftime("%H:%M:%S", time.gmtime(int(duration)))
                else:
                    formatted_duration = time.strftime("%M:%S", time.gmtime(int(duration)))
            else:
                formatted_duration = "LIVE"

            if it == song_index + 1:
                np = self.translator.translate("q_np", guild_id)
                if not live:
                    remaining = self.translator.translate("q_remaining", guild_id)
                    songs = songs + str(it) + f". ♫ {entry.get('title')} <l {formatted_duration} {remaining} l> {np}"
                else:
                    songs = songs + str(it) + f". ♫ {entry.get('title')} <l {formatted_duration} l> {np}"
            else:
                    songs = songs + str(it) + f". ♫ {entry.get('title')} <l {formatted_duration} l>"

            if it == len(meta_list):
                break

            if it == index + 9:
                songs = songs + "\n..."
            else:
                songs = songs + "\n"

            it = it + 1

        return songs

    def build_page(self, guild_id, songs, in_loop, page, last_page):
        return self.translator.translate("q_page", guild_id).format(page_plus=page + 1, last_page_plus = last_page + 1, songs=songs, in_loop = in_loop)

    @commands.command(aliases=['dc', 'quit'], description="ldesc_disconnect", pass_context=True)
    async def disconnect(self, ctx):
        """Desconecta o bot da chamada e encerra tudo"""
        self.verificator.verify_user_voice(ctx)
        self.verificator.verify_bot_voice(ctx)
        self.verificator.verify_same_voice(ctx)

        queue = self.servers_queues.get(ctx.guild.id)

        if queue:
            self.ensure_no_hanging_tasks(queue)
            await self.ensure_now_playing_deleted(queue)
            self.ensure_queue_deleted(ctx.guild.id)

        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        dc_message = await ctx.send(self.translator.translate("dc_msg", ctx.guild.id))
        await dc_message.delete(delay=10)

    def ensure_no_hanging_tasks(self, queue):
        self.cancel_halt_task(queue)
        self.cancel_alone_task(queue)

    async def ensure_now_playing_deleted(self, queue):
        if queue and queue.get('now_playing_message'):
            await queue['now_playing_message'].delete()
            queue['now_playing_message'] = None
    
    def ensure_queue_deleted(self, guild_id):
        if self.servers_queues.get(guild_id):
            self.servers_queues.pop(guild_id)

    @commands.command(aliases=['remover', 'rm'], description="ldesc_remove", pass_context=True)
    async def remove(self, ctx, index : int):
        """Remove alguma música da fila"""
        self.verificator.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)

        songs_list = queue.get('meta_list')
        m_index = index - 1
        if m_index >= len(songs_list):
            raise MoosicError(self.translator.translate("er_rmindex", ctx.guild.id))

        if m_index == queue['song_index']:
            queue['connection'].stop()

        if queue['loop'] == LoopState.LOOP_TRACK:
            if m_index < queue['song_index']:
                queue['song_index'] -= 1
        else:
            if m_index <= queue['song_index']:
                queue['song_index'] -= 1

        songs_list.pop(m_index)
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=['repetir'], description="ldesc_loop", pass_context=True)
    async def loop(self, ctx):
        """Altera o modo de loop do bot"""
        self.verificator.basic_verifications_without_songs(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        mode = ""

        if queue['loop'] == LoopState.NOT_ON_LOOP:
            queue['loop'] = LoopState.LOOP_QUEUE
            mode = self.translator.translate("loop_lq", ctx.guild.id)
        elif queue['loop'] == LoopState.LOOP_QUEUE:
            queue['loop'] = LoopState.LOOP_TRACK
            mode = self.translator.translate("loop_ls", ctx.guild.id)
        elif queue['loop'] == LoopState.LOOP_TRACK:
            queue['loop'] = LoopState.NOT_ON_LOOP
            mode = self.translator.translate("loop_noloop", ctx.guild.id)

        description = self.translator.translate("loop_succ", ctx.guild.id).format(mode=mode)
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        await ctx.send(embed=embed)

        if len(queue['meta_list']) == 0:
            return
 
        if queue['loop'] == LoopState.LOOP_QUEUE and queue['halt_task'] and not queue['halt_task'].cancelled():
            self.cancel_halt_task(queue)
            queue['song_index'] = 0
            await self.play_songs(ctx.guild.id)

    async def get_video(self, id):
        return 

    async def play_songs(self, guild_id):
        queue = self.servers_queues.get(guild_id)
        text_channel = queue.get('text_channel')
        connection = queue.get('connection')

        if not queue['same_song'] and queue.get('now_playing_message'):
            asyncio.create_task(queue['now_playing_message'].delete())
            queue['now_playing_message'] = None

        if not queue['same_song']:
            queue['paused_time'] = None
            queue['elapsed_time'] = None

        if not connection.is_connected():
            return

        if queue.get('song_index') >= len(queue.get('meta_list')):
            queue['halt_task'] = asyncio.ensure_future(self.inactive(guild_id, queue))
            return

        song = queue['meta_list'][queue['song_index']]
        options = Filter.FFMPEG_OPTIONS.copy()

        if not queue['same_song']:
            if song['type'] == MetaType.YOUTUBE:
                video = await Video.get(song.get('id'))
                if song.get("duration"):
                    queue['current_audio_url'] = await self.fetcher.get(video, 251)
                else:
                    queue['current_audio_url'] = video['streamingData']['hlsManifestUrl']

                url=f"https://youtube.com/watch?v={song.get('id')}" 

            elif song['type'] == MetaType.SPOTIFY:
                lookup = (await VideosSearch(song['search_query'], limit=1).next()).get('result')[0]
                video = await Video.get(lookup.get('id'))
                if song.get("duration"):
                    queue['current_audio_url'] = await self.fetcher.get(video, 251)
                else:
                    queue['current_audio_url'] = video['streamingData']['hlsManifestUrl']

                url=song['url']

            duration = song['duration']

            name = self.translator.translate("play_np", guild_id)
            embed=discord.Embed(
                    title=f"{queue.get('song_index') + 1}. {song.get('title')}", 
                    url=url, 
                    description=self.format_duration(duration), 
                    color=0xf57900)
            embed.set_author(name=name)
            embed.set_thumbnail(url=(video).get('thumbnails')[-1].get('url'))
            queue['now_playing_message'] = await text_channel.send(embed=embed)
        else:
            options['before_options'] = f"{options['before_options']} {queue['same_song']['before_options']}"

        connection.play(FFmpegPCMAudio(queue['current_audio_url'], **options), after=partial(self.loop_handler, connection.loop, guild_id, queue))

        if not queue['same_song']:
            queue['elapsed_time'] = time.time()
        else:
            queue['elapsed_time'] = time.time() - queue['same_song']['gap']
            queue['same_song'] = None

    async def inactive(self, guild_id, queue):
        await self.halt(guild_id, queue, 180, self.translator.translate("inactive_notice", guild_id))
        self.cancel_alone_task(queue)

    async def alone(self, guild_id, queue):
        await self.halt(guild_id, queue, 60, self.translator.translate("alone_notice", guild_id))
        self.cancel_halt_task(queue)

    async def halt(self, guild_id, queue, halt_time, reason):
        await asyncio.sleep(halt_time)
        if not self.servers_queues.get(guild_id):
            return

        no_music_message = await queue['text_channel'].send(reason)
        await self.ensure_now_playing_deleted(queue)
        self.ensure_queue_deleted(guild_id)
        await queue['connection'].disconnect()
        await no_music_message.delete(delay=30)

    def loop_handler(self, loop, guild_id, queue, e):
        queue['song_index'] += 1 if not queue['same_song'] and not queue['loop'] == LoopState.LOOP_TRACK else 0

        if queue['loop'] == LoopState.LOOP_QUEUE and queue['song_index'] == len(queue['meta_list']):
            queue['song_index'] = 0

        asyncio.run_coroutine_threadsafe(self.play_songs(guild_id), loop)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        queue = self.servers_queues.get(member.guild.id)

        if queue and member == self.bot.user and not after.channel:
            self.servers_queues.pop(member.guild.id)
            return

        if not queue or member == self.bot.user or (before and after and before.channel == after.channel) or not queue['connection']:
            return

        if len(queue['connection'].channel.members) == 1:
            queue['alone_task'] = asyncio.ensure_future(self.alone(member.guild.id, queue))
        elif queue['alone_task']:
            self.cancel_alone_task(queue)
            if queue['halt_task']:
                self.cancel_halt_task(queue)
                queue['halt_task'] = asyncio.ensure_future(self.inactive(member.guild.id, queue))
