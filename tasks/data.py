import os
import json
from tasks import yandex, youtube, deezer
from datetime import datetime
import time
from settings import STATIC_DIR
from tasks.models import Track, Yandex, Deezer, Youtube


def update_yandex_chart(yandex_chart):
    # Добавление поля deezer_id в yandex_chart

    for yandex_chart_row in yandex_chart:
        if Yandex.get_or_none(Yandex.in_service_id == yandex_chart_row["yandex_id"]) is not None:
            track = Yandex.get(Yandex.in_service_id == yandex_chart_row["yandex_id"]).track
            yandex_chart_row["deezer_id"] = int(Deezer.get(Deezer.track == track).in_service_id)
        else:
            yandex_chart_row["deezer_id"] = deezer.get_deezer_id(yandex_chart_row["artist"], yandex_chart_row["title"])

    with open(f'static/yandex_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(yandex_chart, f)

    return yandex_chart


def update_deezer_chart(deezer_chart):
    # Добавление поля yandex_id в deezer_chart
    for deezer_chart_row in deezer_chart:
        if Deezer.get_or_none(Deezer.in_service_id == deezer_chart_row["deezer_id"]) is not None:
            track = Deezer.get(Deezer.in_service_id == deezer_chart_row["deezer_id"]).track
            deezer_chart_row["yandex_id"] = int(Yandex.get(Yandex.track == track).in_service_id)
        else:
            deezer_chart_row["yandex_id"] = yandex.get_yandex_id(deezer_chart_row["artist"], deezer_chart_row["title"])

    with open(f'static/deezer_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(deezer_chart, f)

    return deezer_chart


def update_general_chart(general_chart, amount_pos):
    # Добавление youtube_id в chart
    for chart_row in general_chart[:amount_pos]:
        if Yandex.get_or_none(Yandex.in_service_id == chart_row["yandex_id"]) is not None:
            track = Yandex.get(Yandex.in_service_id == chart_row["yandex_id"]).track
            if Youtube.get_or_none(Youtube.id == chart_row["youtube_id"]) is None:
                Youtube.create()


            chart_row["youtube_id"] = Youtube.get(Youtube.track == track).id
        else:
            chart_row["youtube_id"] = youtube.get_youtube_id(chart_row["artist"], chart_row["title"])

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


def get_general_chart():
    yandex_chart = yandex.get_chart_info()
    deezer_chart = deezer.get_chart_info()

    yandex_chart = update_yandex_chart(yandex_chart)
    deezer_chart = update_deezer_chart(deezer_chart)

    general_chart = calc_general_chart(yandex_chart, deezer_chart)

    return general_chart


def update_music_base(chart):

    """
    Добавлений новых записей в базу из чарта
    :param music_base:
    :param chart:
    :return:
    """
    for chart_row in chart:
        if Track.get_or_none(Yandex.in_service_id == chart_row["yandex_id"]) is None:
            Track.get_or_create(artist=chart_row["artist"], title=chart_row["title"])
            Yandex.get_or_create(track_id=Track.select(Track.id).order_by(Track.id.desc()).limit(1).get(),
                                 in_service_id=chart_row["yandex_id"], artist=chart_row["artist"],
                                 title=chart_row["title"])
            Deezer.get_or_create(track_id=Track.select(Track.id).order_by(Track.id.desc()).limit(1).get(),
                                 in_service_id=chart_row["deezer_id"], artist=chart_row["artist"],
                                 title=chart_row["title"])
            Youtube.get_or_create(id=chart_row["youtube_id"], title=f'{chart_row["title"]} - {chart_row["artist"]}',
                                  best_part_start=chart_row["video_start"])
            print(f'base.update_music_base(...) The new record, yandex_id: {chart_row["yandex_id"]}')
