import discord
import asyncio
import re

from src.utils.moosic_error import MoosicError
from src.utils.translator import Translator

class MusicVerifications:
    @staticmethod
    def verify_user_voice(ctx):
        if not ctx.author.voice:
            raise MoosicError("er_con")

    @staticmethod
    def verify_bot_voice(ctx):
        if not ctx.voice_client:
            raise MoosicError("er_conb")

    @staticmethod
    def verify_same_voice(ctx):
        if ctx.author.voice and ctx.voice_client and ctx.author.voice.channel != ctx.voice_client.channel:
            raise MoosicError("er_vsv")

    @staticmethod
    def verify_voice(ctx):
        MusicVerifications.verify_user_voice(ctx)
        MusicVerifications.verify_bot_voice(ctx)
        MusicVerifications.verify_same_voice(ctx)

    @staticmethod
    def verify_skip_quantity(how_many):
        try:
            quantity = int(how_many)
        except ValueError:
            raise MoosicError("er_skiparg")

        if how_many <= 0:
            raise MoosicError("er_skipindex")

    @staticmethod
    def verify_perms(ctx):
        channel_permissions = ctx.author.voice.channel.permissions_for(ctx.guild.me)
        if not channel_permissions.connect or not channel_permissions.speak:
            raise MoosicError("er_perm")

    @staticmethod
    def verify_timestamp(timestamp):
        if not re.match('^((?:\d{1,2}:)?(?:\d{1,2}:)?(?:\d{1,2})|\d+)$', timestamp):
            raise MoosicError("er_seekarg")
