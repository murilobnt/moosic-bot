import discord
from discord.ext import commands
from discord.ext.commands.help import HelpCommand
from typing import List, Union

from pretty_help import PrettyHelp
from pretty_help.pretty_help import Paginator
from src.language.translator import Translator

class MoosicPaginator(Paginator):
    def __init__(self, show_index, server_settings, color=0):
        self.translator = Translator(server_settings)
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
        embed = self._new_page(page_title, (self.translator.translate(title.description, guild_id) or "") if cog else "")

        self._add_command_fields(embed, page_title, commands_list, guild_id)

    @staticmethod
    def __command_info(command: Union[commands.Command, commands.Group], translator, guild_id):
        info = ""
        if command.description:
            info += translator.translate(command.description, guild_id) + "\n\n"
        if command.qualified_name:
            info += translator.translate(command.qualified_name, guild_id)
        if not info:
            info = "None"
        return info

    def add_command(self, command: commands.Command, signature: str, guild_id):
        """
        Add a command help page
        Args:
            command (commands.Command): The command to get help for
            signature (str): The command signature/usage string
        """
        desc = f"{command.description}\n\n" if command.description else ""
        page = self._new_page(
            command.qualified_name,
            f"{self.prefix}{self.__command_info(command, self.translator, guild_id)}{self.suffix}" or "",
        )
        if command.aliases:
            aliases = ", ".join(command.aliases)
            page.add_field(
                name="Aliases",
                value=f"{self.prefix}{aliases}{self.suffix}",
                inline=False,
            )
        cooldown: commands.Cooldown = command._buckets._cooldown
        if cooldown:
            page.add_field(
                name="Cooldown",
                value=f"`{cooldown.rate} time(s) every {cooldown.per} second(s)`",
            )

        page.add_field(
            name="Usage", value=f"{self.prefix}{signature}{self.suffix}", inline=False
        )
        self._add_page(page)

    def _add_command_fields(
        self, embed: discord.Embed, page_title: str, commands: List[commands.Command], guild_id
    ):
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

            trans = self.translator.translate(command.name, guild_id)

            embed.add_field(
                name=command.name,
                value=f'{self.prefix}{trans}{self.suffix}',
                inline=False,
            )
        self._add_page(embed)

class MoosicHelp(PrettyHelp):
    def __init__(self, server_settings, **options):
        options['index_title'] = "help_it"
        options['ending_note'] = "help_en"
        super().__init__(**options)
        self.translator = Translator(server_settings)
        self.paginator = MoosicPaginator(
            options.pop("show_index", True), server_settings, self.color
        )

    async def send_bot_help(self, mapping: dict):
        bot = self.context.bot
        channel = self.get_destination()
        guild_id = self.context.guild.id if self.context.guild else -1
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
            self.paginator.add_cog(self.no_category, mapping.pop(None), guild_id)
            sorted_map = sorted(
                mapping.items(),
                key=lambda cg: cg[0].qualified_name
                if isinstance(cg[0], commands.Cog)
                else str(cg[0]),
            )
            for cog, command_list in sorted_map:
                self.paginator.add_cog(cog, command_list, guild_id)
            self.paginator.add_index(self.translator.translate(self.index_title, guild_id), bot)
        await self.send_pages()

    async def send_command_help(self, command: commands.Command):
        filtered = await self.filter_commands([command])
        if filtered:
            self.paginator.add_command(command, self.get_command_signature(command), self.context.guild.id if self.context.guild else -1)
            await self.send_pages()

    def get_ending_note(self, guild_id):
        """Returns help command's ending note. This is mainly useful to override for i18n purposes."""
        note = self.translator.translate(self.ending_note, guild_id) or (
            "Type {help.clean_prefix}{help.invoked_with} command for more info on a command.\n"
            "You can also type {help.clean_prefix}{help.invoked_with} category for more info on a category."
        )
        return note.format(ctx=self.context, help=self if hasattr(self, "clean_prefix") else self.context,)

    async def prepare_help_command(
        self, ctx: commands.Context, command: commands.Command
    ):
        if ctx.guild is not None:
            perms = ctx.channel.permissions_for(ctx.guild.me)
            if not perms.embed_links:
                raise commands.BotMissingPermissions(("embed links",))
            if not perms.read_message_history:
                raise commands.BotMissingPermissions(("read message history",))
            if not perms.add_reactions:
                raise commands.BotMissingPermissions(("add reactions permission",))

        self.paginator.clear()
        self.paginator.ending_note = self.get_ending_note(ctx.guild.id if ctx.guild else -1)
        await HelpCommand.prepare_help_command(ctx, command)
