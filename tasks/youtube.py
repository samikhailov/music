import json
import urllib
import requests
import sys


def get_youtube_id(artist, title):
    print(f'youtube.get_youtube_id("{artist}", "{title}")')
    token = ""
    search_req = urllib.parse.quote_plus(f"{artist} {title}")
    url = (f"https://www.googleapis.com/youtube/v3/search"
           f"?part=snippet&maxResults=1&q={search_req}&key={token}")

    response = requests.get(url)
    data = json.loads(response.text)

    if data.get("error") is not None:
        print("Error.", data["error"]["errors"])
        sys.exit(0)
    elif data["pageInfo"]["totalResults"] == 0:
        print("Video not found.")
        sys.exit(0)
    else:
        result = data["items"][0]["id"]["videoId"]
        print(f'result: {result}')

    return result
