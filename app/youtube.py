import os
import requests
from settings import YOUTUBE_TOKEN


def get_video_id(artist, title):
    token = YOUTUBE_TOKEN
    search = f"{artist} {title}"
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {"part": "snippet", "maxResults": 1, "q": search, "key": token}
    data = requests.get(url, params=params).json()

    if data.get("error"):
        print(data["error"])
        sys.exit(0)
    elif data["pageInfo"]["totalResults"] == 0:
        print("Video not found.")
        sys.exit(0)
    else:
        return data["items"][0]["id"]["videoId"]
