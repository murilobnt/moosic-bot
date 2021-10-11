import discord
from discord.ext import commands
import os

from pretty_help import PrettyHelp
from src.utils.moosic_error import MoosicError
from src.cogs.music_player import MusicPlayer
from src.cogs.server_settings import ServerSettings
from src.language.translator import Translator

intents = discord.Intents.default()
intents.members = True

# Pretty cool, huh?

servers_settings={}

bot = commands.Bot(command_prefix='moo ', help_command=None, intents=intents)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, MoosicError):
        await ctx.send(error)
    raise error

bot.add_cog(ServerSettings(bot, servers_settings))
bot.add_cog(MusicPlayer(bot, servers_settings))
bot.run(os.environ['MOO_BOT_KEY'])
