import logging
import requests
import re
from app import models


def get_chart():
    """
    Метод получения списка лучших треков Deezer.
    """
    logger = logging.getLogger('app.deezer.get_chart')
    url = "https://api.deezer.com/playlist/1116189381"
    data = requests.get(url).json()
    tracks = []
    for position, track in enumerate(data["tracks"]["data"], 1):
        tracks.append(
            models.BaseTrack(
                in_service_id=int(track["id"]),
                title=track["title"],
                artist=track["artist"]["name"],
                position=position,
                service="deezer",
            )
        )
    logger.info("Deezer chart received")
    return tracks


def get_track_id(artist, title):
    logger = logging.getLogger('app.deezer.get_track_id')
    search = re.sub(r"& |Feat. ", "", f"{artist} {title}")
    url = f"https://api.deezer.com/search"
    params = {"q": search}
    data = requests.get(url, params=params).json()
    if data["total"] == 0:
        logger.warning(f"Track not found in Deezer ({artist}, {title})")
        return None
    in_service_id = data["data"][0]["id"]
    logger.info(f"Track found in Deezer ({in_service_id}, {artist}, {title})")
    return in_service_id