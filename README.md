## Moosic Bot

*A simple discord music bot written in Python*

**Moosic** is a bot that born from the passing of groovy. It was a fun 
challenge to embrace. The bot has been used in some private servers for a while,
and although some bugs are still existent, it works!

These are its main features:
* Play a song or a playlist from YouTube or Spotify.
* Basic controls of skipping, pausing, resuming, shuffling, disconnecting,
and seeking.
* Basic information about reproduction queue with now playing, and queue.

This project uses [discord.py](https://github.com/Rapptz/discord.py),
[spotipy](https://spotipy.readthedocs.io/en/master/), and 
[youtube-search-python](https://github.com/alexmercerind/youtube-search-python).

### Requires

- [Python 3](https://www.python.org/)
- Pip (should come installed with Python)

### How to install

#### Step 1: Setup

You first need to set these enviroment variables in order for this bot to
work properly:

- MOO_BOT_KEY : A discord bot application key.
- SP_CLIENT   : Client application key from Spotify.
- SP_SECRET   : Secret application key from Spotify.

Once these are set, it's time to fetch the project's dependencies.

```
python -m pip install -r requirements.txt
```

And it should be enough.

#### Step 2: Executing

Executing is the easiest step.

```
python moosic.py
```

### License

moosic-bot is licensed under the [MIT License](https://github.com/murilobnt/moosic-bot/blob/master/LICENSE).
