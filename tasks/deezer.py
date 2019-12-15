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
    with open("static/music_base.json", "r", encoding="utf-8") as f:
        base = json.load(f)
    for row in base:
        if row["deezer_id"] == deezer_id:
            artist = row["artist"]
            break
    else:
        url = f"https://api.deezer.com/track/{deezer_id}"
        response = requests.get(url)
        data = json.loads(response.text)
        artist = []
        for row in data["contributors"]:
            artist.append(row["name"])
        artist_str = ", ".join(artist)
        print(f'GET deezer artist: {artist_str}')
    return artist


def get_chart_info(amount_pos=20):
    url = "https://api.deezer.com/playlist/1116189381"
    response = requests.get(url)
    data = json.loads(response.text)
    chart = []
    for track in data["tracks"]["data"][:amount_pos]:
        chart.append({})
        chart[-1]["deezer_id"] = track["id"]
        chart[-1]["title"] = track["title"]
        chart[-1]["artist"] = get_artists(track["id"])
        chart[-1]["position"] = len(chart)

    return chart
