import discord
from discord.ext import commands
import os

from pretty_help import PrettyHelp
from src.utils.moosic_error import MoosicError
from src.cogs.music_player import MusicPlayer

intents = discord.Intents.default()
intents.members = True

# Pretty cool, huh?

pretty = PrettyHelp(index_title="Categoria", ending_note="Digite {help.clean_prefix}{help.invoked_with} comando para mais informações sobre o comando.\nAlternativamente, {help.clean_prefix}{help.invoked_with} categoria para mais informações sobre uma categoria.")

bot = commands.Bot(command_prefix='moo ', help_command=pretty, intents=intents)

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
    else:
        raise error

bot.add_cog(MusicPlayer(bot))
bot.run(os.environ['MOO_BOT_KEY'])
