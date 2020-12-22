import logging
import requests
import re
from app.models import BaseTrack


def get_chart():
    """
    Метод получения списка лучших треков Deezer.
    """
    url = "https://api.deezer.com/playlist/1116189381"
    data = requests.get(url).json()
    tracks = []
    for position, track in enumerate(data["tracks"]["data"], 1):
        tracks.append(
            BaseTrack(
                in_service_id=int(track["id"]),
                title=track["title"],
                artist=track["artist"]["name"],
                position=position,
                service="deezer",
            )
        )
    logging.info("Deezer chart received")
    return tracks


def get_track_id(artist, title):
    search = re.sub(r"& |Feat. ", "", f"{artist} {title}")
    url = f"https://api.deezer.com/search"
    params = {"q": search}
    data = requests.get(url, params=params).json()
    if data["total"] == 0:
        logging.warning(f"Track not found in Deezer ({artist}, {title})")
        return None
    logging.info(f"Track found in Deezer ({artist}, {title})")
    return data["data"][0]["id"]