import requests
import json
import urllib


def get_track_id(artist, title):
    print(f'shazam.get_track_id("{artist}", "{title}")')
    search_req = urllib.parse.quote_plus(f"{artist} {title}")
    url = (f"https://www.shazam.com/services/search/v3/ru/RU/web/search"
           f"?query={search_req}&numResults=1&offset=0&types=artists,songs")
    response = requests.get(url)
    data = json.loads(response.text)
    if data == {}:
        return None

    result = data["tracks"]["hits"][0]["key"]
    print(f'result: {result}')
    return result


def get_chart():
    """
    Метод получения списка лучших треков Shazam.
    :return: список словарей, с 5 ключами: shazam_id, artist, title, position, point.
    """
    url = "https://www.shazam.com/shazam/v2/ru/RU/web/-/tracks/country-chart-RU?pageSize=100&startFrom=0"
    response = requests.get(url)
    data = json.loads(response.text)
    chart = []
    for position, track in enumerate(data["chart"], 1):
        chart.append({
            "shazam_id": track["key"],
            "artist": track["heading"]["subtitle"],
            "title": track["heading"]["title"],
            "position": position,
            "point": int(1000 / position)            
        })
    return chart
