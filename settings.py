import os
from dotenv import load_dotenv

load_dotenv()


# Video settings

# Верхняя граница треков в одном чарте
CHART_LIMIT = 50

# Длина одного трека в итоговом чарте
# После изменения удалить все файлы в папке cut_tracks
CHORUS_LENGTH = 8


# Credentials
YOUTUBE_TOKEN = os.getenv("YOUTUBE_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


class Directory:
    root = os.path.dirname(os.path.abspath(__file__))

    static = os.path.join(root, "static")
    soundless_audio = os.path.join(static, "audios", "soundless_mp3")
    font = os.path.join(static, "fonts", "SourceSansPro-Regular.ttf")
    black_image = os.path.join(static, "images", "black.png")
    transparent_image = os.path.join(static, "images", "transparent.png")
    intro_ts = os.path.join(static, "videos", "intro_ts")

    media = os.path.join(root, "media")
    full_tracks = os.path.join(media, "full_tracks")
    cut_tracks = os.path.join(media, "cut_tracks")
    transitions = os.path.join(media, "transitions")
