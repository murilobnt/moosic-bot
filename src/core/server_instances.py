from src.core.moosic_instance import MoosicInstance
from src.operations.disconnector import Disconnector

from src.utils.moosic_error import MoosicError

class ServerInstances:
    def __init__(self, bot):
        self.bot = bot
        self.instances = {}

    def get_instance(self, guild_id):
        instance = self.instances.get(guild_id)
        if not instance:
            raise MoosicError("er_vr")
        return instance

    def create_instance(self, guild_id, text_channel):
        instance = MoosicInstance(self.bot, text_channel, Disconnector(guild_id, self.disconnect))
        self.instances[guild_id] = instance
        return instance

    def get_instance_or_create(self, guild_id, text_channel):
        if self.instances.get(guild_id):
            return self.instances[guild_id]

        return self.create_instance(guild_id, text_channel)

    def disconnect(self, guild_id):
        self.instances.pop(guild_id)
