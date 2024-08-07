import asyncio
import discord
import time
import datetime
import re

from src.utils.moosic_error import MoosicError
from src.utils.enums import LoopState, MoosicSearchType
from src.utils.translator import Translator

class Helpers:

    @staticmethod
    def time_to_seconds(time):
        return (time.hour * 60 + time.minute) * 60 + time.second

    @staticmethod
    def is_int(value):
        try:
            int_value = int(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def str_to_time(time_str):
        time_match = re.search('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$', time_str)
        if time_match.group(1):
            FORMAT = "%H:%M:%S"
        elif time_match.group(2):
            FORMAT = "%M:%S"
        elif time_match.group(3):
            FORMAT = "%S"
        return datetime.datetime.strptime(time_str, FORMAT).time()

    @staticmethod
    def format_duration(duration):
        if not duration:
            return "LIVE"
        if duration >= 3600:
            return time.strftime("%H:%M:%S", time.gmtime(int(duration)))
        else:
            return time.strftime("%M:%S", time.gmtime(int(duration)))

    @staticmethod
    def get_youtube_url_id(youtube_url):
        id_match = re.search('(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
        return id_match.group(1)

    @staticmethod
    def cancel_task(task):
        if task:
            if not task.done():
                task.cancel()

    @staticmethod
    def format_time(time_seconds):
        if time_seconds < 60:
            return (time.strftime("%-Ss", time.gmtime(time_seconds)))
        elif time_seconds < 3600:
            return (time.strftime("%-Mm %-Ss", time.gmtime(time_seconds)))
        else:
            return (time.strftime("%-Hh %-Mm %-Ss", time.gmtime(time_seconds)))

    @staticmethod
    def get_gap_from_timestamp(time_str):
        failed1 = False
        failed2 = False

        try:
            m_time = time.strptime(time_str, "%M:%S")
            gap = datetime.timedelta(minutes=m_time.tm_min, seconds=m_time.tm_sec).seconds
        except:
            failed1 = True

        try:
            m_time = time.strptime(time_str, "%H:%M:%S")
            gap = datetime.timedelta(hours=m_time.tm_hour, minutes=m_time.tm_min, seconds=m_time.tm_sec).seconds
        except:
            failed2 = True

        if failed1 and failed2:
            try:
                gap = int(time_str)
            except:
                print("Should rise an error here (helpers, get_gap_from_timestamp)")

        return gap

    @staticmethod
    def build_q_text(music_list, elapsed, song_index, page):
        songs = ""
        it = 1 + (page * 10)
        index = it

        for entry in music_list[index - 1 : (index - 1) + 10]:
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
                np = Translator.translate("q_np")
                if not live:
                    remaining = Translator.translate("q_remaining")
                    songs = songs + str(it) + f". ♫ {entry.get('title')} <l {formatted_duration} {remaining} l> {np}"
                else:
                    songs = songs + str(it) + f". ♫ {entry.get('title')} <l {formatted_duration} l> {np}"
            else:
                    songs = songs + str(it) + f". ♫ {entry.get('title')} <l {formatted_duration} l>"

            if it == len(music_list):
                break

            if it == index + 9:
                songs = songs + "\n..."
            else:
                songs = songs + "\n"

            it = it + 1

        return songs

    @staticmethod
    def build_q_page(q_text, in_loop, page, last_page):
        return Translator.translate("q_page").format(page_plus=page + 1, last_page_plus = last_page + 1, songs=q_text, in_loop = in_loop)

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
