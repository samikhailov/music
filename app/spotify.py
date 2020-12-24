import requests
import logging
import base64
import os
from settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
from app.models import BaseTrack


def put_access_token_to_env():
    url = "https://accounts.spotify.com/api/token"
    payload = {"grant_type": "client_credentials"}
    b64_auth_str = base64.urlsafe_b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Authorization": f"Basic {b64_auth_str}"}
    data = requests.post(url, data=payload, headers=headers).json()
    os.environ["SPOTIFY_ACCESS_TOKEN"] = data["access_token"]


def get_chart():
    """
    Метод получения списка лучших треков Spotify.
    """
    url = "https://api.spotify.com/v1/playlists/5I4WLaJYpw1pPcRXwUQ9XV"
    params = {"market": "RU", "fields": "tracks.items(track(name,id,artists(name)))"}
    headers = {"Authorization": f"Bearer {os.getenv('SPOTIFY_ACCESS_TOKEN')}"}
    data = requests.get(url, params=params, headers=headers).json()
    tracks = []
    for position, track in enumerate(data["tracks"]["items"], 1):
        tracks.append(
            BaseTrack(
                in_service_id=track["track"]["id"],
                title=track["track"]["name"],
                artist=", ".join([i["name"] for i in track["track"]["artists"]]),
                position=position,
                service="spotify",
            )
        )
    return tracks


def get_track_id(artist, title):
    url = "https://api.spotify.com/v1/search"
    params = {"q": f"{artist} {title}", "type": "track", "market": "RU", "limit": "1"}
    headers = {"Authorization": f"Bearer {os.getenv('SPOTIFY_ACCESS_TOKEN')}"}
    data = requests.get(url, params=params, headers=headers).json()
    if data["tracks"]["items"] == []:
        logging.warning(f"Track not found in Spotify ({artist}, {title})")
        return None
    logging.info(f"Track found in Spotify ({artist}, {title})")
    return data["tracks"]["items"][0]["id"]