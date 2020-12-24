import requests
import logging
import base64
import os
from settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from app import models


def put_access_token_to_env():
    url = "https://accounts.spotify.com/api/token"
    payload = {"grant_type": "client_credentials"}
    b64_auth_str = base64.urlsafe_b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {b64_auth_str}"}
    data = requests.post(url, data=payload, headers=headers).json()
    os.environ["SPOTIFY_ACCESS_TOKEN"] = data["access_token"]


def check_and_update_access_token():
    if os.getenv("SPOTIFY_ACCESS_TOKEN") is None:
        put_access_token_to_env()


def get_chart():
    """
    Метод получения списка лучших треков Spotify.
    """
    logger = logging.getLogger('app.spotify.get_chart')
    check_and_update_access_token()
    url = "https://api.spotify.com/v1/playlists/5I4WLaJYpw1pPcRXwUQ9XV"
    params = {"market": "RU", "fields": "tracks.items(track(name,id,artists(name)))"}
    headers = {"Authorization": f"Bearer {os.getenv('SPOTIFY_ACCESS_TOKEN')}"}
    data = requests.get(url, params=params, headers=headers).json()
    tracks = []
    for position, track in enumerate(data["tracks"]["items"], 1):
        tracks.append(
            models.BaseTrack(
                in_service_id=track["track"]["id"],
                title=track["track"]["name"],
                artist=", ".join([i["name"] for i in track["track"]["artists"]]),
                position=position,
                service="spotify",
            )
        )
    logger.info("Shazam chart received")
    return tracks


def get_track_id(artist, title):
    logger = logging.getLogger('app.spotify.get_track_id')
    check_and_update_access_token()
    url = "https://api.spotify.com/v1/search"
    params = {"q": f"{artist} {title}", "type": "track", "market": "RU", "limit": "1"}
    headers = {"Authorization": f"Bearer {os.getenv('SPOTIFY_ACCESS_TOKEN')}"}
    data = requests.get(url, params=params, headers=headers).json()
    if data["tracks"]["items"] == []:
        logger.warning(f"Track not found in Spotify - {artist}, {title}")
        return None
    in_service_id = data["tracks"]["items"][0]["id"]
    logger.info(f"Track found in Spotify ({in_service_id}, {artist}, {title})")
    return in_service_id