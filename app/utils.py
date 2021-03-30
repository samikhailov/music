import os
import requests
import base64
import logging
from settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(funcName)s: %(message)s",
    datefmt="%H:%M:%S",
)


def spotify_request(func):
    def wrapper(*args, **kwargs):
        if not os.getenv("SPOTIFY_ACCESS_TOKEN"):
            url = "https://accounts.spotify.com/api/token"
            payload = {"grant_type": "client_credentials"}
            b64_auth_str = base64.urlsafe_b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {b64_auth_str}",
            }
            data = requests.post(url, data=payload, headers=headers).json()
            os.environ["SPOTIFY_ACCESS_TOKEN"] = data["access_token"]
        return func(*args, **kwargs)

    return wrapper


def action_log(func):
    def logger(*args, **kwargs):
        logging.info(func.__name__)
        return func(*args, **kwargs)

    return logger

def action_log_track(func):
    def logger(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        logging.info(f"{func.__name__}, {self}, result: {result}")
        return result

    return logger
