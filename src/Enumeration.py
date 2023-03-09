from enum import Enum


class SaveData(Enum):

    DEBUG = 1
    FILE_EXTENSION = 2
    MESSAGES =3

    FILE_PREFIX= 4


class GraphVars(Enum):
    URL = 1
    FOLDER = 2
    VIDEO_OR_PLAYLIST = 3

    AUDIO_OR_VIDEO = 4
    RESOLUTION = 5