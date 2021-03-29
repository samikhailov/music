import requests
import logging
from app import models


def get_chart():
    """
    Метод получения списка лучших треков Shazam.
    """
    logger = logging.getLogger('app.shazam.get_chart')
    url = "https://www.shazam.com/shazam/v2/ru/RU/web/-/tracks/country-chart-RU"
    params = {"pageSize": "100", "startFrom": "0"}
    data = requests.get(url, params=params).json()
    tracks = []
    for position, track in enumerate(data["chart"], 1):
        tracks.append(
            models.BaseTrack(
                in_service_id=int(track["key"]),
                title=track["heading"]["title"],
                artist=track["heading"]["subtitle"],
                position=position,
                service="shazam",
            )
        )
    logger.info("Shazam chart received")
    return tracks


def get_track_id(artist, title):
    logger = logging.getLogger('app.shazam.get_track_id')
    url = "https://www.shazam.com/services/search/v3/ru/RU/web/search"
    params = {"query": f"{artist} {title}", "numResults": "1", "offset": "0", "types":"artists,songs"}
    data = requests.get(url, params=params).json()
    if data == {}:
        logger.warning(f"Track not found in Shazam ({artist}, {title})")
        return None
    in_service_id = int(data["tracks"]["hits"][0]["key"])
    logger.info(f"Track found in Shazam ({in_service_id}, {artist}, {title})")
    return in_service_id