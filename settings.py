import os
from dotenv import load_dotenv

load_dotenv()

# Path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(ROOT_DIR, "static")
MEDIA_DIR = os.path.join(ROOT_DIR, "media")


# Token
YOUTUBE_TOKEN = os.getenv("YOUTUBE_TOKEN")

# Video settings
# Количество треков в одном чарте
CHART_LENGTH = 6
# Длина одного трека в итоговом чарте
ONE_TRACK_LENGTH = 8