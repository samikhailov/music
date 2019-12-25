import json
from tasks import yandex, youtube, deezer
from datetime import datetime
from tasks.models import Track, Yandex, Deezer, Youtube


def update_yandex_chart(yandex_chart):
    """
    Добавление поля deezer_id в yandex_chart
    """
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
    """
    Добавление поля yandex_id в deezer_chart
    """
    for deezer_chart_row in deezer_chart:
        if Deezer.get_or_none(Deezer.in_service_id == deezer_chart_row["deezer_id"]) is None:
            track = Track.get_or_create(artist=deezer_chart_row["artist"], title=deezer_chart_row["title"])
            Deezer.get_or_create(in_service_id=deezer_chart_row["deezer_id"], track=track,
                                 artist=deezer_chart_row["artist"], title=deezer_chart_row["title"])
            yandex_track = yandex.get_yandex_track_info(deezer_chart_row["artist"], deezer_chart_row["title"])
            Yandex.get_or_create(in_service_id=yandex_track["yandex_id"], track=track,
                                 artist=yandex_track["artist"], title=yandex_track["title"])
            print(f"New record. {track.artist} - {track.title}")

        track = Deezer.get(Deezer.in_service_id == deezer_chart_row["deezer_id"]).track
        deezer_chart_row["yandex_id"] = Yandex.get(Yandex.track == track).in_service_id

    with open(f'static/deezer_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(deezer_chart, f)

    return deezer_chart


def update_general_chart(general_chart, amount_pos):
    """
    Добавление youtube_id в general_chart
    """
    for chart_row in general_chart[:amount_pos]:
        track = Yandex.get(Yandex.in_service_id == chart_row["yandex_id"]).track
        if Youtube.get_or_none(Youtube.track == track) is None:
            track_info = youtube.get_youtube_track_info(chart_row["artist"], chart_row["title"])
            Youtube.create(id=track_info["id"], track=track, title=track_info["title"])

        chart_row["youtube_id"] = Youtube.get(Youtube.track == track).id

    return general_chart


def calc_general_chart(yandex_chart, deezer_chart):
    """
    Расчет глобального чата
    """
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
