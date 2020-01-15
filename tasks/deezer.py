import json
import urllib
import requests
from tasks.models import Music


def get_deezer_id(artist, title):
    print(f'deezer.get_deezer_id("{artist}", "{title}")')
    search_req = urllib.parse.quote_plus(f"{artist} {title}")
    url = f"https://api.deezer.com/search?q={search_req}"
    response = requests.get(url)
    data = json.loads(response.text)
    if data["total"] == 0:
        return None

    result = data["data"][0]["id"]
    print(f'result: {result}')
    return result


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
