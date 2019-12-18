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
    url = "https://api.deezer.com/playlist/1116189381"
    response = requests.get(url)
    data = json.loads(response.text)
    chart = []
    for track in data["tracks"]["data"]:
        chart.append({})
        chart[-1]["deezer_id"] = track["id"]
        chart[-1]["title"] = track["title"]
        chart[-1]["artist"] = get_artists(track["id"])
        chart[-1]["position"] = len(chart)
        chart[-1]["point"] = int(1000 / len(chart))

    return chart
