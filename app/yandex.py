import logging
import requests
from app.models import BaseTrack


def get_chart():
    url = "https://music.yandex.ru/handlers/main.jsx"
    params = {"what": "chart", "lang": "ru", "chartType": "tracks"}
    data = requests.get(url, params=params).json()
    tracks = []
    for track in data["chart"]["tracks"]:
        tracks.append(
            BaseTrack(
                in_service_id=int(track["id"]),
                title=track["title"],
                artist=", ".join([i["name"] for i in track["artists"]]),
                position=track["chart"]["position"],
                service="yandex",
            )
        )
    logging.info("Yandex chart received")
    return tracks


def get_track_id(artist, title):
    url = "https://music.yandex.ru/handlers/music-search.jsx"
    params = {"text": f"{artist} {title}", "lang": "ru", "type": "track"}
    data = requests.get(url, params=params).json()
    if data["tracks"]["items"] == []:
        logging.warning(f"Track not found in Yandex ({artist}, {title})")
        return None
    logging.info(f"Track found in Yandex ({artist}, {title})")
    return data["tracks"]["items"][0]["id"]