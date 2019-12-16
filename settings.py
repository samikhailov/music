import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "static")

IMG_DIR = os.path.join(STATIC_DIR, "images")

FONTS_DIR = os.path.join(STATIC_DIR, "fonts")

AUDIOS_DIR = os.path.join(STATIC_DIR, "audios")

VIDEOS_DIR = os.path.join(STATIC_DIR, "videos")

CONTENT_DIR = os.path.join(BASE_DIR, "content")

FULL_VIDEOS_DIR = os.path.join(CONTENT_DIR, "full_videos")

CUT_VIDEOS_DIR = os.path.join(CONTENT_DIR, "cut_videos")

TS_CUT_VIDEOS_DIR = os.path.join(CONTENT_DIR, "ts_cut_videos")

TRANSITION_VIDEOS_DIR = os.path.join(CONTENT_DIR, "transition_videos")

TS_TRANSITION_VIDEOS_DIR = os.path.join(CONTENT_DIR, "ts_transition_videos")

MP3_VIDEOS_DIR = os.path.join(CONTENT_DIR, "mp3_videos")

TASKS_DIR = os.path.join(BASE_DIR, "tasks")
