import discord
import asyncio

from discord.ext import commands

from src.core.server_instances import ServerInstances
from src.utils.helpers import Helpers
from src.utils.music_verifications import MusicVerifications

class MusicPlayer(commands.Cog):
    """desc_mp"""
    def __init__(self, bot):
        self.bot = bot
        self.server_instances = ServerInstances(bot)

    @commands.command(aliases=['p', 't', 'tocar'], description="ldesc_play")
    async def play(self, ctx, *, input : str):
        """Toca uma música, ou um índice de música na fila, e conecta o bot a um canal de voz"""

        MusicVerifications.verify_user_voice(ctx)
        moosic_instance = self.server_instances.get_instance_or_create(ctx.guild.id, ctx.message.channel)

        if Helpers.is_int(input):
            moosic_instance.go_to_song(int(input))
        else:
            await moosic_instance.add_song(ctx.message, input)

        await moosic_instance.connect_to_voice(ctx.author.voice.channel)

        if not moosic_instance.is_playing():
            await moosic_instance.play_current_song()

    @commands.command(aliases=['pular'], description="ldesc_skip")
    async def skip(self, ctx, how_many : int = None):
        """Pula um determinado número de músicas na fila"""

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        MusicVerifications.verify_voice(ctx)

        if how_many:
            MusicVerifications.verify_skip_quantity(how_many)
        else:
            how_many = 1

        moosic_instance.skip(how_many)

    @commands.command(aliases=['time', 'to', 'para', 'em', 'tempo'], description="ldesc_seek")
    async def seek(self, ctx, *, timestamp):
        """Vai para um determinado tempo da música"""

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        MusicVerifications.verify_voice(ctx)
        MusicVerifications.verify_timestamp(timestamp)

        moosic_instance.seek(timestamp)

    @commands.command(aliases=['pausar'], description="ldesc_pause")
    async def pause(self, ctx):
        """Pausa a música que está tocando"""

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        MusicVerifications.verify_voice(ctx)

        moosic_instance.pause()

    @commands.command(aliases=['resumir', 'retomar'], description="ldesc_resume")
    async def resume(self, ctx):
        """Resume a música que estava tocando"""

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        MusicVerifications.verify_voice(ctx)

        moosic_instance.resume()

    @commands.command(aliases=['aleatorio, random'], description="ldesc_shuffle")
    async def shuffle(self, ctx):
        """Reordena a fila de reprodução de forma aleatória"""

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        MusicVerifications.verify_voice(ctx)

        moosic_instance.shuffle()

    @commands.command(aliases=['remover', 'rm'], description="ldesc_remove")
    async def remove(self, ctx, index : int):
        """Remove alguma música da fila"""

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        MusicVerifications.verify_voice(ctx)

        moosic_instance.remove(index)

    @commands.command(aliases=['now_playing', 'tocando_agora', 'ta'], description="ldesc_np")
    async def np(self, ctx):
        """Disponibiliza informações da música que está tocando"""

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        MusicVerifications.verify_voice(ctx)

        await moosic_instance.np(ctx.author.mention, ctx.message.channel)

    @commands.command(aliases=['q', 'fila', 'f', 'cola', 'c'], description="ldesc_queue")
    async def queue(self, ctx):
        """Mostra informações da lista de músicas"""

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        MusicVerifications.verify_voice(ctx)

        await moosic_instance.queue(ctx.message.channel, ctx.author)

    @commands.command(aliases=['repetir'], description="ldesc_loop")
    async def loop(self, ctx):
        """Altera o modo de loop do bot"""

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        MusicVerifications.verify_voice(ctx)

        await moosic_instance.loop(ctx.message.channel)

    @commands.command(aliases=['dc', 'quit'], description="ldesc_disconnect")
    async def disconnect(self, ctx):
        """Desconecta o bot da chamada e encerra tudo"""

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        MusicVerifications.verify_voice(ctx)

        await moosic_instance.do_disconnect(ctx.message.channel)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        moosic_instance = self.server_instances.get_instance(member.guild.id)

        if not moosic_instance or member == self.bot.user or (before and after and before.channel == after.channel):
            return

        if member == self.bot.user and not after.channel:
            self.servers_instances.disconnect(member.guild.id)
            return

        if moosic_instance.discord_stuff.check_alone():
            await moosic_instance.become_alone()
        else:
            moosic_instance.loop_control.cancel_alone()
