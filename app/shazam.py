import requests
import logging
from app.models import BaseTrack


def get_chart():
    """
    Метод получения списка лучших треков Shazam.
    """
    url = "https://www.shazam.com/shazam/v2/ru/RU/web/-/tracks/country-chart-RU"
    params = {"pageSize": "100", "startFrom": "0"}
    data = requests.get(url, params=params).json()
    tracks = []
    for position, track in enumerate(data["chart"], 1):
        tracks.append(
            BaseTrack(
                in_service_id=int(track["key"]),
                title=track["heading"]["title"],
                artist=track["heading"]["subtitle"],
                position=position,
                service="shazam",
            )
        )
    logging.info("Shazam chart received")
    return tracks


def get_track_id(artist, title):
    url = "https://www.shazam.com/services/search/v3/ru/RU/web/search"
    params = {"query": f"{artist} {title}", "numResults": "1", "offset": "0", "types":"artists,songs"}
    data = requests.get(url, params=params).json()
    if data == {}:
        logging.warning(f"Track not found in Shazam ({artist}, {title})")
        return None
    logging.info(f"Track found in Shazam ({artist}, {title})")
    return int(data["tracks"]["hits"][0]["key"])