import discord
from discord.ext import commands

class MoosicBot(commands.Bot):
    async def invoke(self, ctx: commands.Context) -> None:
        """|coro|

        Invokes the command given under the invocation context and
        handles all the internal event dispatch mechanisms.

        Parameters
        -----------
        ctx: :class:`.Context`
            The invocation context to invoke.
        """
        if ctx.command is not None:
            self.dispatch('command', ctx)
            try:
                if await self.can_run(ctx, call_once=True):
                    await ctx.command.invoke(ctx)
                else:
                    raise errors.CheckFailure('The global check once functions failed.')
            except commands.errors.CommandError as exc:
                await ctx.command.dispatch_error(ctx, exc)
            else:
                self.dispatch('command_completion', ctx)
        elif ctx.invoked_with:
            music_player = self.cogs.get("MusicPlayer")
            if not music_player:
                exc = errors.CommandNotFound(f'Command "{ctx.invoked_with}" is not found')
                self.dispatch('command_error', ctx, exc) 
            else:
                ctx.command = music_player.play
                ctx.invoked_with = 'play'
                self.dispatch('command', ctx)
                try:
                    if await self.can_run(ctx, call_once=True):
                        ctx.command._prepare_cooldowns(ctx)
                        await ctx.command(ctx, url=ctx.message.content[4:])
                    else:
                        raise errors.CheckFailure('The global check once functions failed.')
                except commands.errors.CommandError as exc:
                    await ctx.command.dispatch_error(ctx, exc)
