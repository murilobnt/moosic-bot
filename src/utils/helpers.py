import asyncio
import discord
import time

from src.utils.moosic_error import MoosicError
from src.utils.enums import LoopState, MoosicSearchType

class Helpers:
    @staticmethod
    def format_duration(duration):
        if not duration:
            return "LIVE"
        if duration >= 3600:
            return time.strftime("%H:%M:%S", time.gmtime(int(duration)))
        else:
            return time.strftime("%M:%S", time.gmtime(int(duration)))

    @staticmethod
    def cancel_task(task):
        if task:
            if not task.done():
                task.cancel()

    # Mover essas duas funções para outro arquivo
    @staticmethod
    def play_song_index(queue, song_index):
        modifier = 2 if not queue.get('halt_task') and not queue.get('loop') == LoopState.LOOP_TRACK else 1
        url_int = song_index - modifier

        if url_int < 1 - modifier or url_int > len(queue['meta_list']) - modifier:
            raise MoosicError("er_index") # er_index

        queue['song_index'] = url_int

    @staticmethod
    async def connect_and_play(ctx, queue, play_songs):
        try:
            queue['connection'] = await ctx.author.voice.channel.connect()
            await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
            await play_songs(ctx.guild.id)
        except (asyncio.TimeoutError, discord.ClientException) as e:
            raise MoosicError("er_conc")

    @staticmethod
    def build_q_text(guild_id, meta_list, elapsed, song_index, page, translator):
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
                np = translator.translate("q_np", guild_id)
                if not live:
                    remaining = translator.translate("q_remaining", guild_id)
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

    @staticmethod
    def build_q_page(guild_id, songs, in_loop, page, last_page, translator):
        return translator.translate("q_page", guild_id).format(page_plus=page + 1, last_page_plus = last_page + 1, songs=songs, in_loop = in_loop)

    # Deprecated
    @staticmethod
    async def send_added_message(type, queue, translator, guild_id, mention):
        match type:
            case MoosicSearchType.SEARCH_STRING | MoosicSearchType.YOUTUBE_SONG | MoosicSearchType.YOUTUBE_SHORTS | MoosicSearchType.SPOTIFY_SONG:
                cur_song = queue.get('meta_list')[-1]
                description = translator.translate("song_add", guild_id).format(index=len(queue.get('meta_list')), title=cur_song.get('title'), url=cur_song.get('url'), mention=mention)
                embed = discord.Embed(
                        description=description,
                        color=0xcc0000)
                await queue.get('text_channel').send(embed=embed)
            case MoosicSearchType.YOUTUBE_PLAYLIST | MoosicSearchType.SPOTIFY_ALBUM:
                description = translator.translate("pl_add", guild_id).format(pl_len=len(playlist), mention=mention) # BUG! PLAYLIST NOT PASSED
                embed = discord.Embed(
                        description=description,
                        color=0xcc0000)
                await queue.get('text_channel').send(embed=embed)
