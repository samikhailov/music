import json
import urllib
import requests


def get_deezer_id(artist, title):
    search_req = urllib.parse.quote_plus(f"{artist} {title}")
    url = f"https://api.deezer.com/search?q={search_req}"
    response = requests.get(url)
    data = json.loads(response.text)
    print(f'GET deezer_id: {data["data"][0]["id"]}, {artist} - {title}')
    return data["data"][0]["id"]
