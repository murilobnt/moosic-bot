import os
import getopt
import sys

import asyncio
import discord
from discord.ext import commands

from src.cogs.server_settings import ServerSettings
from src.utils.moosic_error import MoosicError
from src.cogs.music_player import MusicPlayer
from src.utils.moosic_help import MoosicHelp

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

discord.utils.setup_logging()

# Pretty cool, huh?

bot = commands.Bot(command_prefix='moo ', help_command=MoosicHelp(), intents=intents)

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
        await bot.add_cog(MusicPlayer(bot))
        await bot.start(os.environ['MOO_BOT_KEY'])

asyncio.run(main())
