import os
import json
from tasks import yandex, youtube, deezer
from datetime import datetime
import time
from settings import STATIC_DIR


def update_yandex_chart(yandex_chart, base):
    # Добавление поля deezer_id в yandex_chart
    for yandex_chart_row in yandex_chart:
        for base_row in base:
            if yandex_chart_row["yandex_id"] == base_row["yandex_id"]:
                yandex_chart_row["deezer_id"] = base_row["deezer_id"]
                break
        else:
            yandex_chart_row["deezer_id"] = deezer.get_deezer_id(yandex_chart_row["artist"], yandex_chart_row["title"])

    with open(f'static/yandex_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(yandex_chart, f)

    return yandex_chart


def update_deezer_chart(deezer_chart, base):
    # Добавление поля yandex_id в deezer_chart
    for deezer_chart_row in deezer_chart:
        for base_row in base:
            if deezer_chart_row["deezer_id"] == base_row["deezer_id"]:
                deezer_chart_row["yandex_id"] = base_row["yandex_id"]
                break
        else:
            deezer_chart_row["yandex_id"] = yandex.get_yandex_id(deezer_chart_row["artist"], deezer_chart_row["title"])

    with open(f'static/deezer_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(deezer_chart, f)

    return deezer_chart


def update_general_chart(general_chart, music_base, amount_pos):
    # Добавление youtube_id в chart
    for chart_row in general_chart[:amount_pos]:
        for music_base_row in music_base:
            if chart_row["yandex_id"] == music_base_row["yandex_id"]:
                if music_base_row.get("youtube_id", "") == "":
                    chart_row["youtube_id"] = youtube.get_youtube_id(chart_row["artist"], chart_row["title"])
                    time.sleep(0.5)
                else:
                    chart_row["youtube_id"] = music_base_row["youtube_id"]

                break

    return general_chart


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


def get_general_chart(base):
    yandex_chart = yandex.get_chart_info()
    deezer_chart = deezer.get_chart_info()

    yandex_chart = update_yandex_chart(yandex_chart, base)
    deezer_chart = update_deezer_chart(deezer_chart, base)

    general_chart = calc_general_chart(yandex_chart, deezer_chart)

    return general_chart


def update_music_base(music_base, chart):
    """
    Добавлений новых записей в базу из чарта
    :param music_base:
    :param chart:
    :return:
    """
    for chart_row in chart:
        for base_row in music_base:
            if base_row["yandex_id"] == chart_row["yandex_id"]:
                base_row["artist"] = base_row.get("artist") or chart_row["artist"]
                base_row["title"] = base_row.get("title") or chart_row["title"]
                base_row["youtube_id"] = base_row.get("youtube_id") or chart_row.get("youtube_id", "")
                base_row["video_start"] = base_row.get("video_start") or chart_row.get("video_start", "")
                base_row["yandex_id"] = base_row.get("yandex_id") or chart_row["yandex_id"]
                base_row["deezer_id"] = base_row.get("deezer_id") or chart_row["deezer_id"]
                print(f'base.update_music_base(...) The record updated, yandex_id: {chart_row["yandex_id"]}')
                break
        else:
            music_base.append({})
            music_base[-1]["artist"] = chart_row["artist"]
            music_base[-1]["title"] = chart_row["title"]
            music_base[-1]["youtube_id"] = chart_row.get("youtube_id", "")
            music_base[-1]["video_start"] = chart_row.get("video_start", "")
            music_base[-1]["yandex_id"] = chart_row["yandex_id"]
            music_base[-1]["deezer_id"] = chart_row["deezer_id"]
            print(f'base.update_music_base(...) The new record, yandex_id: {chart_row["yandex_id"]}')

        with open(os.path.join(STATIC_DIR, "music_base.json"), "w", encoding="utf-8") as f:
            json.dump(music_base, f)

    return music_base
