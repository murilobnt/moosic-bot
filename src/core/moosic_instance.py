import asyncio

from src.operations.music_control import MusicControl
from src.operations.loop_control import LoopControl
from src.operations.discord_stuff import DiscordStuff
from src.operations.disconnector import Disconnector

from src.utils.moosic_finder import MoosicFinder
from src.utils.moosic_error import MoosicError
from src.utils.enums import MoosicSearchType

class MoosicInstance:
    def __init__(self, bot, text_channel, disconnector):
        self.music_control = MusicControl()
        self.loop_control = LoopControl()
        self.discord_stuff = DiscordStuff(bot, text_channel)

        self.disconnector = disconnector
        self.disconnecting = False

    async def connect_to_voice(self, voice_channel):
        await self.discord_stuff.connect_to_voice(voice_channel)

    async def add_song(self, user_message, _input):
        input_type = MoosicFinder.get_input_type(_input)
        song = None
        pl_len = None

        match input_type:
            case MoosicSearchType.YOUTUBE_SONG:
                song = self.music_control.add_youtube_song(_input)
            case MoosicSearchType.YOUTUBE_SHORTS:
                song = self.music_control.add_youtube_shorts_song(_input)
            case MoosicSearchType.YOUTUBE_PLAYLIST:
                pl_len = self.music_control.add_youtube_playlist(_input)
            case MoosicSearchType.SPOTIFY_SONG:
                song = self.music_control.add_spotify_song(_input)
            case MoosicSearchType.SPOTIFY_ALBUM:
                pl_len = self.music_control.add_spotify_album(_input)
            case MoosicSearchType.SEARCH_STRING:
                info = await self.discord_stuff.video_search_query(user_message, _input)
                song = self.music_control.add_youtube_search(info)

        if song:
            await self.discord_stuff.send_new_song_message(song["title"], song["url"], len(self.music_control.music_list), user_message.author.mention, user_message.channel)
        if pl_len:
            await self.discord_stuff.send_new_playlist_message(pl_len, user_message.author.mention, user_message.channel)

    def go_to_song(self, index):
        if index <= 0 or index > len(self.music_control.music_list):
            raise MoosicError("er_index")

        self.music_control.current_index = index - 1

        if self.music_control.playing:
            self.music_control.jump = True
            self.discord_stuff.stop_current_audio()

    def seek(self, timestamp):
        self.music_control.seek(timestamp)
        self.discord_stuff.stop_current_audio()

    def pause(self):
        self.music_control.pause()
        self.discord_stuff.pause()

    def resume(self):
        self.music_control.resume()
        self.discord_stuff.resume()

    def skip(self, how_many):
        self.music_control.skip(how_many)
        self.discord_stuff.stop_current_audio()

    def shuffle(self):
        self.music_control.shuffle()
        if self.music_control.playing:
            self.music_control.jump = True
            self.discord_stuff.stop_current_audio()

    def remove(self, index):
        m_index = index - 1
        current_song = m_index == self.music_control.current_index

        self.music_control.remove(m_index)
        if current_song:
            self.discord_stuff.stop_current_audio()

    async def np(self, mention, text_channel):
        if not self.music_control.playing:
            raise MoosicError("er_npdat")

        elapsed = self.music_control.get_elapsed()
        song = self.music_control.get_current_song()
        position = self.music_control.current_index + 1
        await self.discord_stuff.send_now_playing_message(mention, text_channel, song, position, elapsed)

    async def queue(self, text_channel, author):
        pages = self.music_control.get_queue_pages()
        first_displayed_page = pages[0]
        last_page = pages[1]
        first_message = self.music_control.get_queue_page(first_displayed_page, last_page)

        await self.discord_stuff.send_queue_message(text_channel, author, first_message, first_displayed_page, last_page, lambda page: self.music_control.get_queue_page(page, last_page))

    async def loop(self, text_channel):
        self.music_control.change_loop()
        await self.discord_stuff.send_loop_change_message(text_channel, self.music_control.loop_state)

    def loop_handler(self, loop, e):
        if self.disconnecting:
            return

        if not self.music_control.seeker.on_seek:
            asyncio.run_coroutine_threadsafe(self.next_loop(), loop)
        else:
            asyncio.run_coroutine_threadsafe(self.seek_current_song(), loop)

    async def next_loop(self):
        self.music_control.set_next_index()
        if not self.music_control.reached_end_of_queue():
            await self.play_current_song()
        else:
            self.music_control.playing = False
            await self.loop_control.become_inactive(180, self.disconnect)

    async def play_current_song(self):
        self.music_control.playing = True
        self.loop_control.cancel_inactive()
        await self.discord_stuff.play_song(self.music_control.get_current_song(), self.loop_handler)
        self.music_control.play()
        await self.discord_stuff.delete_now_playing_message()
        await self.discord_stuff.send_music_change_message(self.music_control.get_current_song(), self.music_control.current_index)

    async def seek_current_song(self):
        await self.discord_stuff.seek_current_song(self.music_control.seeker.seek_options, self.loop_handler)
        self.music_control.play()
        self.music_control.seeker.on_seek = False

    def is_playing(self):
        return self.music_control.playing

    async def become_alone(self):
        await self.loop_control.become_alone(60, self.disconnect)

    async def do_disconnect(self, text_channel):
        self.disconnecting = True
        await self.discord_stuff.send_goodbye_message(text_channel)
        await self.disconnect()

    async def disconnect(self):
        await self.discord_stuff.delete_now_playing_message()
        await self.discord_stuff.disconnect()
        self.disconnector.disconnect()
        self.loop_control.cancel_tasks()
