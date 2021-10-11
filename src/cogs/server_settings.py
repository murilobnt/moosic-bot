import discord
from discord.ext import commands

from src.database.async_database import connect_db
from src.database.async_database import create_get_guild_record
from src.language.translator import int_to_sl
from src.utils.moosic_help import MoosicHelp

def is_int(what):
    try:
        int(what)
        return True
    except ValueError:
        return False

class ServerSettings(commands.Cog):
    """desc_ss"""
    def __init__(self, bot, servers_settings):
        self.servers_settings = servers_settings
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.command(aliases=['língua', 'lingua', 'idioma'],
                      short_doc="Stoopid",
                      description="ldesc_language",
                      pass_context=True)

        
    async def language(self, ctx):
        await ctx.send("1. Português\n2. English\n3. Español")
        try:
            opt_msg = await self.bot.wait_for('message', timeout=30, check=lambda message: message.author == ctx.author and is_int(message.content))
        except TimeoutError:
            return
        opt = int(opt_msg.content)
        if opt > 3 or opt < 1:
            return
        conn = await connect_db()
        fetch = await conn.fetchval("SELECT guild_did FROM guild_settings INNER JOIN guilds ON guild_did = guilds.id WHERE guild_id = $1", ctx.guild.id)
        if not fetch:
            guild_did = await create_get_guild_record(conn, ctx.guild.id)
            await conn.execute('''INSERT INTO guild_settings (guild_did, language) VALUES ($1, $2)''', guild_did, opt)
        else:
            await conn.execute('''UPDATE guild_settings SET language = $1 WHERE guild_did = $2''', opt, fetch)

        if not self.servers_settings.get(ctx.guild.id):
            self.servers_settings[ctx.guild.id] = {}

        self.servers_settings[ctx.guild.id]['language'] = int_to_sl(opt)
        self.bot.help_command = MoosicHelp(self.servers_settings)
        await conn.close()
        await opt_msg.add_reaction("\U00002705")

    @commands.Cog.listener()
    async def on_ready(self):
        conn = await connect_db()
        fetch = await conn.fetch("SELECT language, guild_id FROM guild_settings INNER JOIN guilds ON guild_did = guilds.id")
        for language, guild_id in fetch:
            if not self.servers_settings.get(guild_id):
                self.servers_settings[guild_id] = {}
            lang = int_to_sl(language)
            self.servers_settings[guild_id]['language'] = lang

        self.bot.help_command = MoosicHelp(self.servers_settings)
        await conn.close()
