import logging
import requests
from app import models


def get_chart():
    logger = logging.getLogger('app.yandex.get_chart')
    url = "https://music.yandex.ru/handlers/main.jsx"
    params = {"what": "chart", "lang": "ru", "chartType": "tracks"}
    data = requests.get(url, params=params).json()
    tracks = []
    for track in data["chart"]["tracks"]:
        tracks.append(
            models.BaseTrack(
                in_service_id=int(track["id"]),
                title=track["title"],
                artist=", ".join([i["name"] for i in track["artists"]]),
                position=track["chart"]["position"],
                service="yandex",
            )
        )
    logger.info("Yandex chart received")
    return tracks


def get_track_id(artist, title):
    # TODO: сделать проверку на ответ по названию трека. На запрос 
    # "shut/off Feat. SLAVA MARLOW, Всё в порядке" выдает полную хрень.
    logger = logging.getLogger('app.yandex.get_track_id')
    url = "https://music.yandex.ru/handlers/music-search.jsx"
    params = {"text": f"{artist} {title}", "lang": "ru", "type": "track"}
    data = requests.get(url, params=params).json()
    if data["tracks"]["items"] == []:
        logger.warning(f"Track not found in Yandex ({artist}, {title})")
        return None
    in_service_id = data["tracks"]["items"][0]["id"]
    logger.info(f"Track found in Yandex ({in_service_id}, {artist}, {title})")
    return in_service_id