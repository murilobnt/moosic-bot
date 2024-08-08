from typing import Optional, Any
from discord.ext import commands

from src.utils.translator import Translator

class MoosicError(commands.CommandError):
    def __init__(self, message: Optional[str] = None, *args: Any):
        super().__init__(Translator.translate(message), *args)
