import discord
from discord.ext import commands
import os
import getopt, sys

from pretty_help import PrettyHelp
from src.utils.moosic_error import MoosicError
from src.cogs.music_player import MusicPlayer
from src.language.translator import Translator

try:
    opts, args = getopt.getopt(sys.argv[1:], "", ["no-database"])
except getopt.GetoptError as err:
    print("Option not recognized")
    sys.exit(2)

use_db = True
for o, _ in opts:
    if o == "--no-database":
        print("No database mode enabled.")
        use_db = False

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

if use_db:
    from src.cogs.server_settings import ServerSettings
    bot.add_cog(ServerSettings(bot, servers_settings))
bot.add_cog(MusicPlayer(bot, servers_settings))
bot.run(os.environ['MOO_BOT_KEY'])
