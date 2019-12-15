import json
import urllib
import requests
import sys


def get_youtube_id(artist, title):
    token = "AIzaSyAlFQEDZ_eupQyAw7HksR8AYT7cBYAYsYA"
    search_req = urllib.parse.quote_plus(f"{artist} {title}")
    url = (f"https://www.googleapis.com/youtube/v3/search"
           f"?part=snippet&maxResults=1&q={search_req}&key={token}")
    response = requests.get(url)
    data = json.loads(response.text)
    if data.get("error") is not None:
        print("Error.", data["error"]["errors"])
        sys.exit(0)
    elif data["pageInfo"]["totalResults"] == 0:
        result = ""
    else:
        result = data["items"][0]["id"]["videoId"]
        print(f"GET youtube_id: {result}, {artist} - {title}")
    return result
