import os
import json
import requests
from yandex_music.client import Client


def get_client():
    """
    Метод авторизации в yandex music.
    :return: объект класса Client.
    """
    path = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(path, "credentials_yandex.json"), "r") as f:
            credentials = json.load(f)
        client = Client.from_token(credentials["token"])
    except:
        client = Client.from_credentials(credentials["login"], credentials["password"])
        credentials["token"] = client.token
        with open("credentials_yandex.json", "w") as f:
            json.dump(credentials, f)
    return client


def get_yandex_id(artist, title):
    client = get_client()
    request = client.search(f"{artist} {title}")
    print(f"Updated. yandex_id: {request.best.result.id}, {artist} - {title}")
    return str(request.best.result.id)


def get_chart_info(amount_pos):
    """
    Метод получения списка лучших треков.
    :return: список словарей, с 4 ключами: yandex_id, title, artist, position.
    """
    url = ("https://music.yandex.ru/handlers/main.jsx"
           "?what=chart&chartType=&lang=ru&external-domain=music.yandex.ru&overembed=false")

    response = requests.get(url)
    data = json.loads(response.text)
    chart = []
    for track in data["chart"]["tracks"][:amount_pos]:
        chart.append({})
        chart[-1]["yandex_id"] = track["id"]
        chart[-1]["title"] = track["title"]
        chart[-1]["artist"] = ", ".join([i["name"] for i in track["artists"]])
        chart[-1]["position"] = track["chart"]["position"]

    return chart
