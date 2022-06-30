def time_to_seconds(time):
    return (time.hour * 60 + time.minute) * 60 + time.second

def str_to_time(time_str):
    time_match = re.match('^(?:(?:([01]?\d|2[0-3]):)?([0-5]?\d):)?([0-5]?\d)$', time_str)
    if time_match.group(1):
        FORMAT = "%H:%M:%S"
    elif time_match.group(2):
        FORMAT = "%M:%S"
    elif time_match.group(3):
        FORMAT = "%S"
    return datetime.datetime.strptime(time_str, FORMAT).time()

def format_duration(self, duration):
    if not duration:
        return "LIVE"
    if duration >= 3600:
        return time.strftime("%H:%M:%S", time.gmtime(int(duration)))
    else:
        return time.strftime("%M:%S", time.gmtime(int(duration)))

def cancel_task(self, task):
    if task:
        if not task.done():
            task.cancel()

        task = None

# Mover essas duas funções para outro arquivo
def play_song_index(self, queue, song_index):
    modifier = 2 if not queue.get('halt_task') and not queue.get('loop') == LoopState.LOOP_TRACK else 1
    url_int = song_index - modifier

    if url_int < 1 - modifier or url_int > len(queue['meta_list']) - modifier:
        raise MoosicError("TODO: ERRO") # er_index
        #raise MoosicError(self.translator.translate("er_index", ctx.guild.id))

    queue['song_index'] = url_int

async def connect_and_play(self, ctx, queue):
    try:
        queue['connection'] = await ctx.author.voice.channel.connect()
        await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
        #await self.play_songs(ctx.guild.id)
    except (asyncio.TimeoutError, discord.ClientException) as e:
        #self.ensure_queue_deleted(ctx.guild.id)
        #raise MoosicError(self.translator.translate("er_conc", ctx.guild.id))
