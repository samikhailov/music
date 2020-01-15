import json
import urllib
import requests
from tasks.models import Deezer


def get_deezer_id(artist, title):
    search_req = urllib.parse.quote_plus(f"{artist} {title}")
    url = f"https://api.deezer.com/search?q={search_req}"
    response = requests.get(url)
    data = json.loads(response.text)
    if data["total"] == 0:
        result = hash(f"{artist} {title}")
        if result > 0:
            result *= -1
    else:
        result = data["data"][0]["id"]
    print(f'deezer.get_deezer_id("{artist}", "{title}"): {result}, ')
    return result


def get_artists(deezer_id):
    if Deezer.get_or_none(Deezer.in_service_id == deezer_id) is not None:
        artist = Deezer.get_or_none(Deezer.in_service_id == deezer_id).artist
    else:
        url = f"https://api.deezer.com/track/{deezer_id}"
        response = requests.get(url)
        data = json.loads(response.text)
        artist = []
        for row in data["contributors"]:
            artist.append(row["name"])
        artist = ", ".join(artist)
        print(f'deezer.get_artists({deezer_id}): "{artist}"')
    return artist


def get_chart_info():
    """
    Метод получения списка лучших треков Deezer.
    :return: список словарей, с 5 ключами: deezer_id, title, artist, position, point.
    """
    url = "https://api.deezer.com/playlist/1116189381"
    response = requests.get(url)
    data = json.loads(response.text)
    chart = []
    for position, track in enumerate(data["tracks"]["data"], 1):
        chart.append({
            "deezer_id": track["id"],
            "title": track["title"],
            "artist": track["artist"]["name"],
            "position": position,
            "point": int(1000 / position)
        })
    return chart
