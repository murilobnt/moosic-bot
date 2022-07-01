## Moosic Bot

*A simple discord music bot written in Python*

**Moosic** is a bot that born from the passing of groovy. It was a fun 
challenge to embrace. The bot have been used in around four servers for a while,
and although some bugs are still existent, it works!

These are its main features:
* Play a song or a playlist from YouTube or Spotify.
* Basic controls of skipping, pausing, resuming, shuffling, disconnecting,
and seeking.
* Basic information about reproduction queue with now playing, and queue.
* Supports three languages: Portuguese, English and Spanish.

This project uses [discord.py](https://github.com/Rapptz/discord.py) and 
[youtube-search-python](https://github.com/alexmercerind/youtube-search-python).

### Requires

- [Python3](https://www.python.org/)
- Pip (should come installed with Python)
- (PostgreSQL)[https://www.postgresql.org/]

### How to install

#### Step 1: Import DB Schema

*NOTE: ALL DATABASE RELATED STEPS OR SUBSTEPS CAN BE SKIPPED IF YOU WISH NOT TO 
USE THE DATABASE. SEE STEP 3.*

To import the SQL schema:

```
[postgres] createdb moosic
```

This will create the database moosic. Then, to import the schema of this
project:

```
$ psql -U postgres -d moosic "database.sql"
```

#### Step 2: Enviroment variables

You first need to set these enviroment variables in order for this bot to
work properly:

- MOO_BOT_KEY : A discord bot application key.
- DATABASE_URL: An url to the PostgreSQL database. It follows a structure similar
to "postgresql://user:password@host:port/database"
- SP_CLIENT   : Client application key from Spotify.
- SP_SECRET   : Secret application key from Spotify.

Once these are set, it's time to fetch the project's dependencies.

```
python3 -m pip install -r requirements.txt
```

And it should be enough.

#### Step 3: Executing

Executing is the easiest step.

```
python moosic.py
```

In case you had trouble setting up the database, you might want to execute, 
instead:

```
python devmoosic.py
```

**However, the language of the bot will only be available in portuguese.**

### License

moosic-bot is licensed under the [MIT License](https://github.com/murilobnt/moosic-bot/blob/master/LICENSE).


