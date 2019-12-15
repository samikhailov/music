import json
from tasks import yandex, youtube, deezer
from datetime import datetime


def append_yandex_chart(yandex_chart, base):
    # Добавление поля deezer_id в yandex_chart
    for yandex_chart_row in yandex_chart:
        for base_row in base:
            if yandex_chart_row["yandex_id"] == base_row["yandex_id"]:
                yandex_chart_row["deezer_id"] = base_row["deezer_id"]
                break
        else:
            yandex_chart_row["deezer_id"] = deezer.get_deezer_id(yandex_chart_row["artist"], yandex_chart_row["title"])

    return yandex_chart


def append_deezer_chart(deezer_chart, base):
    # Добавление поля yandex_id в deezer_chart
    for deezer_chart_row in deezer_chart:
        for base_row in base:
            if deezer_chart_row["deezer_id"] == base_row["deezer_id"]:
                deezer_chart_row["yandex_id"] = base_row["yandex_id"]
                break
        else:
            deezer_chart_row["yandex_id"] = deezer.get_deezer_id(deezer_chart_row["artist"], deezer_chart_row["title"])

    return deezer_chart


def calc_general_chart(yandex_chart, deezer_chart):
    # Расчет глобального чата
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

    with open(f'static/general_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(general_chart, f)

    return general_chart


def get_general_chart():
    with open("static/music_base.json", "r", encoding="utf-8") as f:
        base = json.load(f)

    yandex_chart = yandex.get_chart_info()
    deezer_chart = deezer.get_chart_info()

    yandex_chart = append_yandex_chart(yandex_chart, base)
    deezer_chart = append_deezer_chart(deezer_chart, base)

    general_chart = calc_general_chart(yandex_chart, deezer_chart)

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
            music_base[-1]["youtube_id"] = chart_row.get("youtube_id", "")
            music_base[-1]["yandex_id"] = chart_row["yandex_id"]
            music_base[-1]["deezer_id"] = chart_row["deezer_id"]
            print(f'New record in the base. id: {music_base[-1]["id"]}')
    return music_base
