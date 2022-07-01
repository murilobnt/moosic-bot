import discord
import asyncio
import random
import time
import traceback
import os
import spotipy
import datetime

from spotipy.oauth2 import SpotifyClientCredentials
from discord import FFmpegPCMAudio, PCMVolumeTransformer
from youtubesearchpython.__future__ import Video, Playlist, VideosSearch, StreamURLFetcher
from discord.ext import commands

from enum import Enum
from functools import partial

from src.utils.music_verifications import MusicVerifications
from src.utils.moosic_error import MoosicError
from src.utils.moosic_finder import MetaType, InteractiveText, MoosicFinder
from src.utils.helpers import Helpers, LoopState
from src.language.translator import Translator

class Filter:
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


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

    @commands.command(aliases=['p', 't', 'tocar'], description="ldesc_play", pass_context=True)
    async def play(self, ctx, *, input : str):
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
            queue = {
                        'text_channel'        : ctx.message.channel,
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
            self.servers_queues[ctx.guild.id] = queue

        song_index = None
        try:
            song_index = int(input)
        except ValueError:
            pass
        
        try:
            if song_index:
                self.verificator.verify_connection(ctx, queue)
                self.verificator.verify_no_songs(ctx, queue)
                try:
                    Helpers.play_song_index(queue, song_index)
                    if not queue.get('halt_task'):
                        queue['connection'].stop()
                except MoosicError as e:
                    raise MoosicError(self.translator.translate("er_index"), ctx.guild.id)
            else:
                async def send_and_choose(choose_text):
                    choice_picker = await ctx.message.channel.send(self.translator.translate("play_buildt", ctx.guild.id).format(songs_str=choose_text))
                    try:
                        response = await self.bot.wait_for('message', \
                                                           timeout=30, \
                        check=lambda message: message.author == ctx.message.author and \
                        message.channel == ctx.message.channel)
                        return InteractiveText(choice_picker, response)
                    except asyncio.TimeoutError:
                        await choice_picker.delete()
                        raise MoosicError(self.translator.translate("er_shtimeout", ctx.guild.id))

                try:
                    type = await MoosicFinder.input_to_meta(input, queue['meta_list'], self.sp, send_and_choose)
                    await Helpers.send_added_message(type, queue, self.translator, ctx.guild.id, ctx.author.mention)
                except MoosicError as e:
                    raise MoosicError(self.translator.translate(str(e), ctx.guild.id)) # This can't be a good practice!
        except:
            if created_queue:
                self.ensure_queue_deleted(ctx.guild.id)
            raise

        if created_queue:
            try:
                await Helpers.connect_and_play(ctx, queue, self.play_songs)
            except:
                self.ensure_queue_deleted(ctx.guild.id)
                raise MoosicError(self.translator.translate("er_conc", ctx.guild.id))
        elif queue.get('halt_task'):
            Helpers.cancel_task(queue['halt_task'])
            await self.play_songs(ctx.guild.id)

    @commands.command(aliases=['pular'], description="ldesc_skip", pass_context=True) 
    async def skip(self, ctx, *, how_many : int = None):
        """Pula um determinado número de músicas na fila"""
        self.verificator.basic_verifications(ctx)
        queue = self.servers_queues.get(ctx.guild.id)
        self.verificator.verify_is_playing(queue, ctx.guild.id)
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
        self.verificator.verify_is_playing(queue, ctx.guild.id)

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
        self.verificator.verify_is_playing(queue, ctx.guild.id)

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
        self.verificator.verify_is_playing(queue, ctx.guild.id)

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

        msg = await ctx.send(Helpers.build_q_page(ctx.guild.id, Helpers.build_q_text(ctx.guild.id, meta_list, elapsed, song_index, page, self.translator), in_loop, page, last_page, self.translator))
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

                    await msg.edit(content=Helpers.build_q_page(ctx.guild.id, Helpers.build_q_text(ctx.guild.id, meta_list, elapsed, song_index, page), in_loop, page, last_page))
                    await msg.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "◀️":
                    page -= 1
                    if page < 0:
                        page = last_page
                    await msg.edit(content=Helpers.build_q_page(ctx.guild.id, Helpers.build_q_text(ctx.guild.id, meta_list, elapsed, song_index, page), in_loop, page, last_page))
                    await msg.remove_reaction(reaction, user)
                else:
                    await msg.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                break

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
                    description=Helpers.format_duration(duration), 
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
        Helpers.cancel_task(queue['alone_task'])

    async def alone(self, guild_id, queue):
        await self.halt(guild_id, queue, 60, self.translator.translate("alone_notice", guild_id))
        Helpers.cancel_task(queue['halt_task'])

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
