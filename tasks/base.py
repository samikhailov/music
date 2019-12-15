import json
from tasks import yandex, youtube, deezer


def calc_chart(amount_pos=20):
    yandex_chart = yandex.get_chart_info(amount_pos)
    for row in yandex_chart:
        row["point"] = int(100 / row["position"])

    deezer_chart = deezer.get_chart_info(amount_pos)
    for row in deezer_chart:
        row["point"] = int(100 / row["position"])

    with open("static/music_base.json", "r", encoding="utf-8") as f:
        base = json.load(f)

    for yandex_chart_row in yandex_chart:
        for base_row in base:
            if yandex_chart_row["yandex_id"] == base_row["yandex_id"]:
                yandex_chart_row["deezer_id"] = base_row["deezer_id"]
                break
        else:
            yandex_chart_row["deezer_id"] = deezer.get_deezer_id(yandex_chart_row["artist"], yandex_chart_row["title"])

    for deezer_chart_row in deezer_chart:
        for base_row in base:
            if deezer_chart_row["deezer_id"] == base_row["deezer_id"]:
                deezer_chart_row["yandex_id"] = base_row["yandex_id"]
                break
        else:
            deezer_chart_row["yandex_id"] = deezer.get_deezer_id(deezer_chart_row["artist"], deezer_chart_row["title"])

    general_chart = yandex_chart.copy()
    for deezer_chart_row in deezer_chart:
        for general_chart_row in general_chart:
            if general_chart_row["deezer_id"] == deezer_chart_row["deezer_id"]:
                general_chart_row["point"] += deezer_chart_row["point"]
                break
        else:
            general_chart.append(deezer_chart_row)

    general_chart.sort(key=lambda dictionary: dictionary['point'], reverse=True)
    for row in enumerate(general_chart, 1):
        row[1]["position"] = row[0]

    general_chart = general_chart[:amount_pos]
    general_chart.sort(key=lambda dictionary: dictionary['position'], reverse=True)

    return general_chart


def append_music_base(music_base, chart):
    """
    Добавлений новых записей в базу из чарта
    :param music_base:
    :param chart:
    :return:
    """
    for chart_row in chart:
        for base_row in music_base:
            if chart_row["yandex_id"] == base_row["yandex_id"]:
                break
        else:
            music_base.append({})
            music_base[-1]["id"] = len(music_base)
            music_base[-1]["artist"] = chart_row["artist"]
            music_base[-1]["title"] = chart_row["title"]
            music_base[-1]["yandex_id"] = chart_row["yandex_id"]
            print(f'New record in the base. id: {music_base[-1]["id"]}')
    return music_base


def update_music_base(music_base):
    """
    Пополнение базы полями yandex_id и youtube_id по API.
    :param music_base:
    :return:
    """
    for row in music_base:
        if row.get("yandex_id") is None or row.get("yandex_id") == "":
            row["yandex_id"] = yandex.get_yandex_id(row["artist"], row["title"])

        if row.get("youtube_id") is None or row.get("youtube_id") == "":
            row["youtube_id"] = youtube.get_youtube_id(row["artist"], row["title"])

    return music_base


def update_chart(music_base, chart):
    """
    Пополнение чарта полями id и youtube_id из базы.
    :param music_base:
    :param chart:
    :return:
    """
    for chart_row in chart:
        for base_row in music_base:
            if chart_row["yandex_id"] == base_row["yandex_id"]:
                chart_row["id"] = base_row["id"]
                chart_row["youtube_id"] = base_row["youtube_id"]
    return chart
