import discord
import asyncio

from src.utils.moosic_error import MoosicError
from src.utils.translator import Translator

class MusicVerifications:
    @staticmethod
    def verify_user_voice(self, ctx):
        if not ctx.author.voice:
            raise MoosicError(Translator.translate("er_con"))

    @staticmethod
    def verify_bot_voice(self, ctx):
        if not ctx.voice_client:
            raise MoosicError(Translator.translate("er_conb"))

    @staticmethod
    def verify_same_voice(self, ctx):
        if ctx.author.voice and ctx.voice_client and ctx.author.voice.channel != ctx.voice_client.channel:
            raise MoosicError(Translator.translate("er_vsv"))
