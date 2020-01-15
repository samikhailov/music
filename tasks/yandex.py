import os
import json
import requests
from yandex_music.client import Client
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
    print(f'yandex.get_yandex_id("{artist}", "{title}")')
    client = get_client()
    response = client.search(f"{artist} {title}")
    if response.best is None:
        return None
    result = response.best.result.id
    print(f'result: {result}')
    return result


def get_chart_info():
    """
    Метод получения списка лучших треков Яндекс Музыки.
    :return: список словарей, с 5 ключами: yandex_id, title, artist, position, point.
    """
    url = ("https://music.yandex.ru/handlers/main.jsx"
           "?what=chart&chartType=&lang=ru&external-domain=music.yandex.ru&overembed=false")

    response = requests.get(url)
    data = json.loads(response.text)
    chart = []
    for track in data["chart"]["tracks"]:
        chart.append({
            "yandex_id": track["id"],
            "title": track["title"],
            "artist": ", ".join([i["name"] for i in track["artists"]]),
            "position":  track["chart"]["position"],
            "point": int(1000 / track["chart"]["position"])
        })

    return chart
