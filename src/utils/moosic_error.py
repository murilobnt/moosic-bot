from typing import Optional, Any
from discord.ext import commands

class MoosicError(commands.CommandError):
    def __init__(self, message: Optional[str] = None, *args: Any):
        super().__init__(message, *args)
