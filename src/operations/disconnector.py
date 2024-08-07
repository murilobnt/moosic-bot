class Disconnector:
    def __init__(self, guild_id, destroy_callback):
        self.guild_id = guild_id
        self.destroy_callback = destroy_callback

    def disconnect(self):
        self.destroy_callback(self.guild_id)
