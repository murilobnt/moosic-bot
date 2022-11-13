import os
import getopt
import sys

import asyncio
import discord
from discord.ext import commands

from src.cogs.server_settings import ServerSettings
from src.utils.moosic_error import MoosicError
from src.cogs.music_player import MusicPlayer

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
intents.message_content = True
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

async def main():
    async with bot:
        if use_db:
            await bot.add_cog(ServerSettings(bot, servers_settings))
        await bot.add_cog(MusicPlayer(bot, servers_settings))
        await bot.start(os.environ['MOO_BOT_KEY'])

asyncio.run(main())
