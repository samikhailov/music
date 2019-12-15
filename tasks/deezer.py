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


def get_artists(deezer_id):
    url = f"https://api.deezer.com/track/{deezer_id}"
    response = requests.get(url)
    data = json.loads(response.text)
    artists = []
    for row in data["contributors"]:
        artists.append(row["name"])

    return ", ".join(artists)


def get_chart_info():
    url = "https://api.deezer.com/playlist/1116189381"
    response = requests.get(url)
    data = json.loads(response.text)
    chart = []
    for track in data["tracks"]["data"]:
        chart.append({})
        chart[-1]["deezer_id"] = track["id"]
        chart[-1]["title"] = track["title"]
        # chart[-1]["artist"] = ", ".join([i["name"] for i in track["artists"]])
        chart[-1]["position"] = len(chart)

    return chart