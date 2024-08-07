from enum import Enum

class LoopState(Enum):
    NOT_ON_LOOP = 1
    LOOP_QUEUE = 2
    LOOP_TRACK = 3

class MetaType(Enum):
    YOUTUBE = 1
    SPOTIFY = 2

class MoosicSearchType(Enum):
    SEARCH_STRING = 1
    YOUTUBE_SONG = 2
    YOUTUBE_SHORTS = 3
    YOUTUBE_PLAYLIST = 4
    SPOTIFY_SONG = 5
    SPOTIFY_ALBUM = 6
    UNKNOWN = 7

class LoopIntent(Enum):
    NORMAL = 1
    SEEK = 2

