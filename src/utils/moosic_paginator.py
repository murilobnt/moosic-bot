import discord
from discord.ext import commands
from typing import List, Union

from pretty_help import PrettyHelp
from pretty_help.pretty_help import Paginator
from src.language.translator import Translator

class MoosicPaginator(Paginator):
    def __init__(self, show_index, servers_settings, color=0):
        self.servers_settings = servers_settings
        self.translator = Translator(servers_settings)
        super().__init__(show_index, color)

    def add_cog(
        self, title: Union[str, commands.Cog], commands_list: List[commands.Command], guild_id
    ):
        """
        Add a cog page to the help menu

        Args:
            title (Union[str, commands.Cog]): The title of the embed
            commands_list (List[commands.Command]): List of commands
        """
        cog = isinstance(title, commands.Cog)
        if not commands_list:
            return

        page_title = title.qualified_name if cog else title
        embed = self._new_page(page_title, (title.description or "") if cog else "")

        self._add_command_fields(embed, page_title, commands_list, guild_id)

    def _add_command_fields(
        self, embed: discord.Embed, page_title: str, commands: List[commands.Command], guild_id
    ):
        print(f"NO FLIPPING WAY {guild_id}")
        """
        Adds command fields to Category/Cog and Command Group pages

        Args:
            embed (discord.Embed): The page to add command descriptions
            page_title (str): The title of the page
            commands (List[commands.Command]): The list of commands for the fields
        """
        for command in commands:
            if not self._check_embed(
                embed,
                self.ending_note,
                command.name,
                command.short_doc,
                self.prefix,
                self.suffix,
            ):

                self._add_page(embed)
                embed = self._new_page(page_title, embed.description)

            embed.add_field(
                name=command.name,
                value=f'{self.prefix}{command.short_doc or "No Description"}{self.suffix}',
                inline=False,
            )
        self._add_page(embed)

class MoosicHelp(PrettyHelp):
    def __init__(self, servers_settings, **options):
        super().__init__(**options)
        self.paginator = MoosicPaginator(
            show_index=options.pop("show_index", True), servers_settings=servers_settings, color=self.color
        )

    async def send_bot_help(self, mapping: dict):
        bot = self.context.bot
        channel = self.get_destination()
        async with channel.typing():
            mapping = {name: [] for name in mapping}
            help_filtered = (
                filter(lambda c: c.name != "help", bot.commands)
                if len(bot.commands) > 1
                else bot.commands
            )
            for cmd in await self.filter_commands(
                help_filtered,
                sort=self.sort_commands,
            ):
                mapping[cmd.cog].append(cmd)
            self.paginator.add_cog(self.no_category, mapping.pop(None), self.context.guild.id)
            sorted_map = sorted(
                mapping.items(),
                key=lambda cg: cg[0].qualified_name
                if isinstance(cg[0], commands.Cog)
                else str(cg[0]),
            )
            for cog, command_list in sorted_map:
                self.paginator.add_cog(cog, command_list, self.context.guild.id)
            self.paginator.add_index(self.index_title, bot)
        await self.send_pages()
