import discord
import asyncio

from src.utils.moosic_error import MoosicError
from src.language.translator import Translator

class MusicVerifications:
    def __init__(self, translator, servers_queues):
        self.translator = translator
        self.servers_queues = servers_queues

    def basic_verifications(self, ctx):
        self.basic_verifications_without_songs(ctx)
        self.verify_no_songs(ctx, self.servers_queues.get(ctx.guild.id))

    def basic_verifications_without_songs(self, ctx):
        self.verify_registry(ctx)
        self.verify_same_voice(ctx)

    def verify_is_playing(self, queue):
        if queue['song_index'] >= len(queue['meta_list']):
            raise MoosicError(self.translator.translate("er_nosong", ctx.guild.id))

    def verify_user_voice(self, ctx):
        if not ctx.author.voice:
            raise MoosicError(self.translator.translate("er_con", ctx.guild.id))

    def verify_bot_voice(self, ctx):
        if not ctx.voice_client:
            raise MoosicError(self.translator.translate("er_conb", ctx.guild.id))

    def verify_connection(self, ctx, queue):
        if not queue.get('connection'):
            raise MoosicError(self.translator.translate("er_conb", ctx.guild.id))

    def verify_info_fields(self, info):
        if not info.get('title') or not info.get('url'):
            raise MoosicError(self.translator.translate("er_down", ctx.guild.id))

    def verify_same_voice(self, ctx):
        if ctx.author.voice and ctx.voice_client and ctx.author.voice.channel != ctx.voice_client.channel:
            raise MoosicError(self.translator.translate("er_vsv", ctx.guild.id))

    def verify_registry(self, ctx):
        if not self.servers_queues.get(ctx.guild.id):
            raise MoosicError(self.translator.translate("er_vr", ctx.guild.id))

    def verify_no_songs(self, ctx, queue):
        if not queue.get('meta_list'):
            raise MoosicError(self.translator.translate("er_vns", ctx.guild.id))

