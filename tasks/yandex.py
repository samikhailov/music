import os
import json
import requests
from yandex_music.client import Client
from datetime import datetime
from settings import TASKS_DIR


def get_client():
    """
    Метод авторизации в yandex music.
    :return: объект класса Client.
    """
    try:
        with open(os.path.join(TASKS_DIR, "credentials_yandex.json"), "r", encoding="utf-8") as f:
            credentials = json.load(f)
        client = Client.from_token(credentials["token"])
    except:
        client = Client.from_credentials(credentials["login"], credentials["password"])
        credentials["token"] = client.token
        with open(os.path.join(TASKS_DIR, "credentials_yandex.json"), "w", encoding="utf-8") as f:
            json.dump(credentials, f)
    return client


def get_yandex_id(artist, title):
    client = get_client()
    request = client.search(f"{artist} {title}")
    result = request.best.result.id
    print(f'yandex.get_yandex_id("{artist}", "{title}"): {result}')
    return result


def get_chart_info():
    """
    Метод получения списка лучших треков.
    :return: список словарей, с 4 ключами: yandex_id, title, artist, position.
    """
    url = ("https://music.yandex.ru/handlers/main.jsx"
           "?what=chart&chartType=&lang=ru&external-domain=music.yandex.ru&overembed=false")

    response = requests.get(url)
    data = json.loads(response.text)
    chart = []
    for track in data["chart"]["tracks"]:
        chart.append({})
        chart[-1]["yandex_id"] = int(track["id"])
        chart[-1]["title"] = track["title"]
        chart[-1]["artist"] = ", ".join([i["name"] for i in track["artists"]])
        chart[-1]["position"] = track["chart"]["position"]
        chart[-1]["point"] = int(1000 / track["chart"]["position"])

    return chart
