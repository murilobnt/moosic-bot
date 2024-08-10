import asyncio
from functools import partial

import discord
from discord import FFmpegPCMAudio

import time

from src.utils.moosic_finder import MoosicFinder, InteractiveText
from src.utils.moosic_grabber import MoosicGrabber
from src.utils.moosic_error import MoosicError
from src.utils.helpers import Helpers

from src.utils.enums import MetaType, LoopState
from src.utils.translator import Translator

from youtubesearchpython import VideosSearch

class Filter:
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class DiscordStuff:
    def __init__(self, bot, text_channel):
        self.bot = bot
        self.text_channel = text_channel
        self.vc_conn = None

        self.current_audio_url = None
        self.current_video_thumbnail = None
        self.now_playing_message = None

    async def connect_to_voice(self, voice_channel):
        if self.vc_conn and self.vc_conn.is_connected():
            return

        try:
            self.vc_conn = await voice_channel.connect()
            await voice_channel.guild.change_voice_state(channel=voice_channel, self_deaf=True)
        except (asyncio.TimeoutError, discord.ClientException) as e:
            raise MoosicError("er_conc")

    async def video_search_query(self, message, query):
        entries = MoosicFinder.search_youtube(query)

        choice_picker = await message.channel.send(Translator.translate("play_buildt").format(songs_str=Helpers.build_choose_text(entries)))
        try:
            response = await self.bot.wait_for('message', \
                                               timeout=30, \
            check=lambda choice_message: choice_message.author == message.author and \
            choice_message.channel == message.channel)
            interactive_text = InteractiveText(choice_picker, response)
        except asyncio.TimeoutError:
            await choice_picker.delete()
            raise MoosicError("er_shtimeout")

        try:
            choice = int(interactive_text.response.content)
        except ValueError:
            await interactive_text.sent_text.delete()
            raise MoosicError("play_shcancel")
        if choice < 1 or choice > len(entries):
            await interactive_text.sent_text.delete()
            raise MoosicError("er_shoutlen")
        info = entries[choice - 1]
        await interactive_text.sent_text.delete()

        return info

    async def send_new_song_message(self, title, url, index, mention, text_channel):
        description = Translator.translate("song_add").format(index=index, title=title, url=url, mention=mention)
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        await text_channel.send(embed=embed)

    async def send_new_playlist_message(self, pl_length, mention, text_channel):
        description = Translator.translate("pl_add").format(pl_len=pl_length, mention=mention)
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        await text_channel.send(embed=embed)

    async def send_now_playing_message(self, mention, text_channel, song, position, elapsed):
        duration = song.get('duration')
        formatted_elapsed = Helpers.format_time(elapsed)

        if duration and duration != 0:
            formatted_duration = Helpers.format_time(duration)

            completion_bar = int((elapsed/duration) * 20)
            complement_bar = 20 - completion_bar

            progress_bar = '' + "▮"*completion_bar + "▯"*complement_bar
            description = Translator.translate("np_succnorm").format(index=position, title=song.get('title'), weburl=song.get('url'), mention=mention, progress_bar=progress_bar, formatted_elapsed=formatted_elapsed, formatted_duration=formatted_duration)
            embed = discord.Embed(
                    description=description,
                    color=0xedd400)
            await text_channel.send(embed=embed)
        else:
            description = Translator.translate("np_succlive").format(index=position, title=song.get('title'), weburl=song.get('url'), mention=mention, formatted_elapsed=formatted_elapsed)
            embed = discord.Embed(
                    description=description,
                    color=0xedd400)
            await text_channel.send(embed=embed)
    
    async def send_queue_message(self, text_channel, author, content, page, last_page, get_content):
        msg = await text_channel.send(content)

        if last_page > 0:
            await msg.add_reaction("◀️")
            await msg.add_reaction("▶️")

        def check(reaction, user):
            return user == author and str(reaction.emoji) in ["◀️", "▶️"]

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)

                if str(reaction.emoji) == "▶️":
                    page += 1
                    if page > last_page:
                        page = 0

                    await msg.edit(content=get_content(page))
                    await msg.remove_reaction(reaction, user)
                elif str(reaction.emoji) == "◀️":
                    page -= 1
                    if page < 0:
                        page = last_page
                    await msg.edit(content=get_content(page))
                    await msg.remove_reaction(reaction, user)
                else:
                    await msg.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                break

    async def send_loop_change_message(self, text_channel, loop_state):
        if loop_state == LoopState.NOT_ON_LOOP:
            mode = Translator.translate("loop_noloop")
        elif loop_state == LoopState.LOOP_QUEUE:
            mode = Translator.translate("loop_lq")
        elif loop_state == LoopState.LOOP_TRACK:
            mode = Translator.translate("loop_ls")
        else:
            return # error

        description = Translator.translate("loop_succ").format(mode=mode)
        embed = discord.Embed(
                description=description,
                color=0xcc0000)
        await text_channel.send(embed=embed)

    async def send_music_change_message(self, song, index):
        name = Translator.translate("play_np")
        embed=discord.Embed(
                title=f"{index + 1}. {song.get('title')}",
                url=song.get('url'),
                description=Helpers.format_duration(song.get('duration')),
                color=0xf57900)
        embed.set_author(name=name)
        embed.set_thumbnail(url=self.current_video_thumbnail)
        self.now_playing_message = await self.text_channel.send(embed=embed)

    async def send_goodbye_message(self, text_channel):
        dc_message = await text_channel.send(Translator.translate("dc_msg"))
        await dc_message.delete(delay=10)

    async def delete_now_playing_message(self):
        if self.now_playing_message:
            asyncio.create_task(self.now_playing_message.delete())

    async def play_song(self, song, loop_handler):
        if not self.vc_conn.is_connected():
            return
        
        options = Filter.FFMPEG_OPTIONS.copy()

        if song['type'] == MetaType.YOUTUBE:
            video = MoosicGrabber.request_yt(song.get('id'))
        elif song['type'] == MetaType.SPOTIFY:
            lookup = (VideosSearch(song['search_query'], limit=1).result()).get('result')[0]
            video = MoosicGrabber.request_yt(lookup.get('id'))

        self.current_audio_url = video.get_audio_url()
        self.current_video_thumbnail = video.get_thumbnail()
        self.vc_conn.play(FFmpegPCMAudio(self.current_audio_url, **options), after=partial(loop_handler, self.vc_conn.loop))

    async def seek_current_song(self, before_options, loop_handler):
        options = Filter.FFMPEG_OPTIONS.copy()
        options['before_options'] = f"{options['before_options']} {before_options}"

        self.vc_conn.play(FFmpegPCMAudio(self.current_audio_url, **options), after=partial(loop_handler, self.vc_conn.loop))

    def check_alone(self):
        return self.vc_conn and len(self.vc_conn.channel.members) == 1

    # Will stop the audio and call the "after" function, which should be moosic_instance.loop_handler
    def stop_current_audio(self):
        self.vc_conn.stop()

    def pause(self):
        self.vc_conn.pause()

    def resume(self):
        self.vc_conn.resume()

    async def disconnect(self):
        await self.vc_conn.disconnect()
