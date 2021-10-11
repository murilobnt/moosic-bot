import discord
import youtube_dl
import asyncio
import time
import re
import datetime
import validators

from discord import FFmpegPCMAudio, PCMVolumeTransformer
from discord.ext import commands
from enum import Enum
from functools import partial
from urllib.parse import urlparse, parse_qs

from src.utils.moosic_error import MoosicError
from src.database.async_database import create_get_guild_record
from src.language.translator import Translator

class Filter:
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

class LoopState(Enum):
    NOT_ON_LOOP = 1
    LOOP_QUEUE = 2
    LOOP_TRACK = 3

class MusicPlayer(commands.Cog):
    """desc_mp"""
    def __init__(self, bot, servers_settings):
        self.bot = bot
        self.servers_queues = {}
        self.translator = Translator(servers_settings)
        self.ytdl = youtube_dl.YoutubeDL({'format'         : 'bestaudio/best', 
                                          'source_address' : '0.0.0.0', 
                                          'cookiefile'     : 'cookies.txt',
                                          'noplaylist'     : True, 
                                          'extract_flat'   : True})

        try:
            self.ytdl.cache.remove()
        except youtube_dl.DownloadError as e:
            pass

    def verify_user_voice(self, ctx):
        if not ctx.author.voice:
            raise MoosicError(self.translator.translate("er_con", ctx.guild.id))

    def verify_connection(self, queue):
        if not queue.get('connection'):
            raise MoosicError(self.translator.translate("er_conb", ctx.guild.id))

    def verify_info_fields(self, info):
        if not info.get('title') or not info.get('url'):
            raise MoosicError(self.translator.translate("er_down", ctx.guild.id))

    async def play_song_index(self, ctx, queue, song_index):
        modifier = 2 if not queue.get('halt_task') and not queue.get('loop') == LoopState.LOOP_TRACK else 1
        url_int = song_index - modifier

        if url_int < 1 - modifier or url_int > len(queue['meta_list']) - modifier:
            raise MoosicError(self.translator.translate("er_index", ctx.guild.id))

        queue['song_index'] = url_int

    async def handle_on_playlist_url(self, guild_id, queue, info, author_mention):
        return
        parsed_query = parse_qs(urlparse(info.get('webpage_url')).query)
        if not parsed_query or not parsed_query.get('v'):
            raise MoosicError(self.translator.translate("er_ytdl", ctx.guild.id))
        info = self.ytdl.extract_info("https://youtube.com/watch?v=bruh", download=False)
        self.verify_info_fields(info)
        await self.enqueue_song(guild_id, queue, info, author_mention)

    async def handle_input(self, guild_id, queue, url, author_mention):
        if validators.url(url):
            # url handling
            try:
                info = self.ytdl.extract_info(url, download=False)
            except Exception:
                print(traceback.format_exc())
                raise MoosicError(self.translator.translate("er_url", guild_id))

            if info.get('_type') and info.get('_type') == 'playlist':
                await self.enqueue_playlist(guild_id, queue, info['entries'], author_mention)
            elif info.get('_type') and info.get('_type') == 'url' and info.get('extractor_key') and info.get('extractor_key') == 'YoutubeTab':
                await self.handle_on_playlist_url(guild_id, queue, info, author_mention)
            else:
                self.verify_info_fields(info)
                await self.enqueue_song(guild_id, queue, info, author_mention)
        else:
            # search handling
            try:
                info = self.ytdl.extract_info(f"ytsearch:{url}", download=False).get('entries')[0]
            except Exception:
                print(traceback.format_exc())
                raise MoosicError(self.translator.translate("er_url", guild_id))

            self.verify_info_fields(info)
            await self.enqueue_song(guild_id, queue, info, author_mention)

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
        self.verify_user_voice(ctx)

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
                self.verify_connection(queue)
                self.verify_no_songs(queue)
                await self.play_song_index(ctx, queue, song_index)
                if not queue.get('halt_task'):
                    queue['connection'].stop()
            else:
                await self.handle_input(ctx.guild.id, queue, url, ctx.author.mention)
        except MoosicError as e:
            if created_queue:
                self.servers_queues.pop(ctx.guild.id)
            raise e

        if created_queue:
            await self.connect_and_play(ctx, queue)
        else:
            if queue['halt_task']:
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

    async def enqueue_song(self, guild_id, queue, info, mention):
            meta = { 'title'    : info.get('title'),
                     'url'      : f"https://youtube.com/watch?v={info.get('id')}",
                     'duration' : info.get('duration')
                    }
            queue['meta_list'].append(meta)
            description = self.translator.translate("song_add", guild_id).format(title=meta.get('title'), url=meta.get('url'), mention=mention)
            embed = discord.Embed(
                    description=description,
                    color=0xcc0000)
            await queue['text_channel'].send(embed=embed)
    
    async def enqueue_playlist(self, guild_id, queue, playlist_items, mention):
        for item in playlist_items:
            meta = { 'title'    : item.get('title'),
                     'url'      : f"https://youtube.com/watch?v={item.get('url')}",
                     'duration' : item.get('duration')
                    }
            queue['meta_list'].append(meta)

        description = self.translator.translate("pl_add", guild_id).format(pl_len=len(playlist_items))
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        await queue['text_channel'].send(embed=embed)

    def basic_verifications(self, ctx):
        self.basic_verifications_without_songs(ctx)
        self.verify_no_songs(self.servers_queues.get(ctx.guild.id))

    def basic_verifications_without_songs(self, ctx):
        self.verify_registry(ctx)
        self.verify_same_voice(ctx)

    def verify_is_playing(self, queue):
        if queue['song_index'] >= len(queue['meta_list']):
            raise MoosicError(self.translator.translate("er_nosong", ctx.guild.id))

    @commands.command(aliases=['pular'], description="ldesc_skip", pass_context=True) 
    async def skip(self, ctx, *, how_many : int = None):
        """Pula um determinado número de músicas na fila"""
        self.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        self.verify_is_playing(queue)
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
        await ctx.send(embed=embed)

        queue['connection'].stop()

    @commands.command(aliases=['pausar'], description="ldesc_pause", pass_context=True)
    async def pause(self, ctx):
        """Pausa a música que está tocando"""
        self.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        self.verify_is_playing(queue)

        if queue.get('paused_time'):
            raise MoosicError(self.translator.translate("er_paused", ctx.guild.id))

        queue['paused_time'] = time.time()
        queue['connection'].pause()
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=['resumir'], description="ldesc_resume", pass_context=True)
    async def resume(self, ctx):
        """Resume a música que estava tocando"""
        self.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        self.verify_is_playing(queue)

        if not queue.get('paused_time'):
            raise MoosicError(self.translator.translate("er_nopause", ctx.guild.id))

        queue['elapsed_time'] = queue['elapsed_time'] + (time.time() - queue['paused_time'])
        queue['paused_time'] = None

        queue['connection'].resume()
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=['time', 'to', 'para', 'em', 'tempo'], description="ldesc_seek", pass_context=True)
    async def seek(self, ctx, timestamp : str):
        """Vai para um determinado tempo da música"""
        self.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)

        if not re.match('^(\d{1,2}:)?(\d{1,2}:)?(\d{1,2})$', timestamp) and not re.match('^\d+$', timestamp):
            raise MoosicError(self.translator.translate("er_seekarg", ctx.guild.id))

        failed1 = False
        failed2 = False

        try:
            m_time = time.strptime(timestamp, "%M:%S")
            gap = datetime.timedelta(minutes=m_time.tm_min, seconds=m_time.tm_sec).seconds
        except:
            failed1 = True

        try:
            m_time = time.strptime(timestamp, "%H:%M:%S")
            gap = datetime.timedelta(hours=m_time.tm_hour, minutes=m_time.tm_min, seconds=m_time.tm_sec).seconds
        except:
            failed2 = True
        
        if failed1 and failed2:
            gap = int(timestamp)

        queue['same_song'] = {'gap': gap, 'options': f"-vn -ss {timestamp}"} 
        queue['connection'].stop()
        await ctx.message.add_reaction("\U00002705")

    @commands.command(aliases=['now_playing', 'tocando_agora', 'ta'], description="ldesc_np", pass_context=True)
    async def np(self, ctx):
        """Disponibiliza informações da música que está tocando"""
        self.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        self.verify_is_playing(queue)

        if not queue['elapsed_time']:
            raise MoosicError(self.translator.translate("er_npdat", ctx.guild.id))

        now = time.time()
        time_paused = now - queue['paused_time'] if queue['paused_time'] else 0
        elapsed = int((now - queue['elapsed_time']) - time_paused)
        duration = queue['meta_list'][queue['song_index']]['duration']
            
        if elapsed < 60:
            formatted_elapsed = (time.strftime("%-Ss", time.gmtime(elapsed)))
        elif elapsed < 3600:
            formatted_elapsed = (time.strftime("%-Mm %-Ss", time.gmtime(elapsed)))
        else:
            formatted_elapsed = (time.strftime("%-Hh %-Mm %-Ss", time.gmtime(elapsed)))

        live = True if duration == 0 else False
        if not live:
            if duration < 60:
                formatted_duration = (time.strftime("%-Ss", time.gmtime(duration)))
            elif duration < 3600:
                formatted_duration = (time.strftime("%-Mm %-Ss", time.gmtime(duration)))
            else:
                formatted_duration = (time.strftime("%-Hh %-Mm %-Ss", time.gmtime(duration)))

        song = queue['meta_list'][queue['song_index']]

        if not live:
            completion_bar = int((elapsed/duration) * 20)
            complement_bar = 20 - completion_bar

            progress_bar = '' + "▮"*completion_bar + "▯"*complement_bar
            description = self.translator.translate("np_succnorm", ctx.guild.id).format(title=song.get('title'), weburl=song.get('web_url'), mention=ctx.author.mention, progress_bar=progress_bar, formatted_elapsed=formatted_elapsed, formatted_duration=formatted_duration)
            embed = discord.Embed(
                    description=description,
                    color=0xedd400)
            await ctx.send(embed=embed)
        else:
            description = self.translator.translate("np_succlive", ctx.guild.id).format(title=song.get('title'), weburl=song.get('web_url'), mention=ctx.author.mention, formatted_elapsed=formatted_elapsed)
            embed = discord.Embed(
                    description=description,
                    color=0xedd400)
            await ctx.send(embed=embed)

    @commands.command(aliases=['q', 'fila'], description="ldesc_queue", pass_context=True)
    async def queue(self, ctx):
        """Mostra informações da lista de músicas"""
        self.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)

        meta_list = queue['meta_list'][:]
        page = 0
        last_page = int((len(meta_list) - 1) / 10)

        now = time.time()
        time_paused = now - queue['paused_time'] if queue['paused_time'] else 0
        elapsed = int((now - queue['elapsed_time']) - time_paused) if queue['elapsed_time'] else 0
        song_index = queue['song_index']

        il_index = "q_norep" if queue['loop'] == LoopState.NOT_ON_LOOP else "qrep" if queue['loop'] == LoopState.LOOP_QUEUE else "q_songrep" if queue['loop'] == LoopState.LOOP_TRACK else ":P"
        in_loop = ""

        if il_index == "q_songrep":
            in_loop = self.translator.translate(il_index, ctx.guild.id).format(song=queue['meta_list'][queue['song_index']]['title']) if queue['song_index'] < len(queue['meta_list']) else self.translator.translate("q_next", ctx.guild.id)
        elif il_index == ":P":
            in_loop = ":P"
        else:
            in_loop = self.translator.translate(il_index, ctx.guild.id)

        songs = self.build_text(ctx.guild.id, meta_list, elapsed, song_index, page)
        current_page = self.build_page(ctx.guild.id, songs, in_loop, page, last_page)

        msg = await ctx.send(self.build_page(ctx.guild.id, songs, in_loop, page, last_page))
        if page == last_page:
            return
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
                    songs = self.build_text(meta_list, elapsed, song_index, page)
                    await msg.edit(content=self.build_page(ctx.guild.id, songs, in_loop, page, last_page))
                    await msg.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "◀️":
                    page -= 1
                    if page < 0:
                        page = last_page
                    songs = self.build_text(meta_list, elapsed, song_index, page)
                    await msg.edit(content=self.build_page(ctx.guild.id, songs, in_loop, page, last_page))
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
            live = True if entry['duration'] == 0 else False

            if not live:
                if it == song_index + 1 and page == 0:
                    duration = entry['duration'] - elapsed
                else:
                    duration = entry['duration']

                if duration >= 3600:
                    formatted_duration = time.strftime("%H:%M:%S", time.gmtime(int(duration)))
                else:
                    formatted_duration = time.strftime("%M:%S", time.gmtime(int(duration)))
            else:
                formatted_duration = "LIVE"

            songs = songs + str(it) + f". {entry.get('title')}, {formatted_duration}"
            if it == song_index + 1 and page == 0:
                if not live:
                    songs = songs + self.translator.translate("q_np", guild_id)
                else:
                    songs = songs + self.translator.translate("q_nplive", guild_id)

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
        self.verify_same_voice(ctx)
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

    def verify_same_voice(self, ctx):
        if ctx.author.voice and ctx.voice_client and ctx.author.voice.channel != ctx.voice_client.channel:
            raise MoosicError(self.translator.translate("er_vsv", ctx.guild.id))

    def verify_registry(self, ctx):
        if not self.servers_queues.get(ctx.guild.id):
            raise MoosicError(self.translator.translate("er_vr", ctx.guild.id))

    def verify_no_songs(self, queue):
        if not queue.get('meta_list'):
            raise MoosicError(self.translator.translate("er_vns", ctx.guild.id))

    @commands.command(aliases=['remover', 'rm'], description="ldesc_remove", pass_context=True)
    async def remove(self, ctx, index : int):
        """Remove alguma música da fila"""
        self.basic_verifications(ctx)
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
        self.basic_verifications_without_songs(ctx)
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

    async def play_songs(self, guild_id):
        queue = self.servers_queues.get(guild_id)
        text_channel = queue.get('text_channel')
        connection = queue.get('connection')

        if not queue['same_song'] and queue.get('now_playing_message'):
            await queue['now_playing_message'].delete()
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
            try:
                to_play = self.ytdl.extract_info(song.get("url"), download=False)
            except youtube_dl.utils.DownloadError:
                await text_channel.send(self.translator.translate("er_playdl", guild_id).format(title=song['title']))

                await self.loop_handler(connection.loop, guild_id, queue, None)
                return

            duration = song['duration']
            live = True if duration == 0 else False
            if not live:
                if duration >= 3600:
                    formatted_duration = time.strftime("Duração: %H:%M:%S", time.gmtime(int(duration)))
                else:
                    formatted_duration = time.strftime("Duração: %M:%S", time.gmtime(int(duration)))
            else:
                formatted_duration = "LIVE"

            queue['current_audio_url'] = to_play.get('formats')[0].get('url')

            name = self.translator.translate("play_np", guild_id)
            embed=discord.Embed(
                    title=song.get('title'), 
                    url=to_play.get('url'), 
                    description=formatted_duration, 
                    color=0xf57900)
            embed.set_author(name=name)
            embed.set_thumbnail(url=to_play.get('thumbnails')[-1].get('url'))
            queue['now_playing_message'] = await text_channel.send(embed=embed)
        else:
            options['options'] = queue['same_song']['options']

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
        await self.halt(guild_id, queue, 60, aself.translator.translate("alone_notice", guild_id))
        self.cancel_halt_task(queue)

    async def halt(self, guild_id, queue, halt_time, reason):
        await asyncio.sleep(halt_time)
        if not self.servers_queues.get(guild_id):
            return

        no_music_message = await queue['text_channel'].send(reason)
        self.servers_queues.pop(guild_id)
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
