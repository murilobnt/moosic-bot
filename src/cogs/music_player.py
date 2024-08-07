import discord
import asyncio

from discord.ext import commands

from src.core.server_instances import ServerInstances
from src.utils.helpers import Helpers

class MusicPlayer(commands.Cog):
    """desc_mp"""
    def __init__(self, bot):
        self.bot = bot
        self.server_instances = ServerInstances(bot)

    @commands.command(aliases=['p', 't', 'tocar'], description="ldesc_play")
    async def play(self, ctx, *, input : str):
        """Toca uma música, ou um índice de música na fila, e conecta o bot a um canal de voz"""

        if not ctx.author.voice:
            return

        moosic_instance = self.server_instances.get_instance_or_create(ctx.guild.id, ctx.message.channel)

        if Helpers.is_int(input):
            moosic_instance.go_to_song(int(input))
        else:
            await moosic_instance.add_song(ctx.message, input)

        await moosic_instance.connect_to_voice(ctx.author.voice.channel)
        if not moosic_instance.is_playing():
            await moosic_instance.play_current_song()

    @commands.command()
    async def skip(self, ctx, how_many : int = None):
        if how_many:
            if how_many <= 0:
                return # error
        else:
            how_many = 1

        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        moosic_instance.skip(how_many)

    @commands.command()
    async def seek(self, ctx, *, timestamp):
        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        moosic_instance.seek(timestamp)

    @commands.command()
    async def pause(self, ctx):
        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        moosic_instance.pause()

    @commands.command()
    async def resume(self, ctx):
        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        moosic_instance.resume()

    @commands.command()
    async def shuffle(self, ctx):
        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        moosic_instance.shuffle()

    @commands.command()
    async def remove(self, ctx, index : int):
        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        moosic_instance.remove(index)

    @commands.command()
    async def np(self, ctx):
        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        await moosic_instance.np(ctx.author.mention, ctx.message.channel)

    # Also harder
    @commands.command()
    async def queue(self, ctx):
        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        await moosic_instance.queue(ctx.message.channel, ctx.author)

    # Needs text feedback to user
    @commands.command()
    async def loop(self, ctx):
        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
        await moosic_instance.loop(ctx.message.channel)

    @commands.command(aliases=["dc"])
    async def disconnect(self, ctx):
        moosic_instance = self.server_instances.get_instance(ctx.guild.id)
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
