import json
from tasks import yandex, youtube, deezer
from datetime import datetime
from tasks.models import Music
from tasks import video


def update_video_start(mp3_video, youtube_id):
    start_video = video.get_video_start(mp3_video, clip_length=8)
    track = Music.get(youtube_id=youtube_id)
    track.video_start = start_video
    track.save()
    return track


def insert_track(track, service):
    if service == "yandex":
        track["deezer_id"] = deezer.get_deezer_id(track["artist"], track["title"])
    elif service == "deezer":
        track["yandex_id"] = yandex.get_yandex_id(track["artist"], track["title"])
    else:
        return None

    track_object = Music.create(
        artist=track["artist"],
        title=track["title"],
        yandex_id=track["yandex_id"],
        deezer_id=track["deezer_id"]
    )

    return track_object


def update_yandex_chart(yandex_chart):
    """
    Добавление поля deezer_id в yandex_chart
    """
    for yandex_chart_row in yandex_chart:
        track = Music.get_or_none(Music.yandex_id == yandex_chart_row["yandex_id"])
        if track is None:
            track = insert_track(yandex_chart_row, "yandex")
        yandex_chart_row["deezer_id"] = track.deezer_id

    with open(f'static/yandex_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(yandex_chart, f)

    return yandex_chart


def update_deezer_chart(deezer_chart):
    """
    Добавление поля yandex_id в deezer_chart
    """
    for deezer_chart_row in deezer_chart:
        track = Music.get_or_none(Music.deezer_id == deezer_chart_row["deezer_id"])
        if track is None:
            track = insert_track(deezer_chart_row, "deezer")
        deezer_chart_row["yandex_id"] = track.yandex_id

    with open(f'static/deezer_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(deezer_chart, f)

    return deezer_chart


def update_general_chart(general_chart, amount_pos):
    """
    Добавление youtube_id в general_chart
    """
    for track in general_chart[:amount_pos]:
        track_object = Music.get_or_none(Music.yandex_id == track["yandex_id"])
        if track_object is None:
            track_object = Music.get(Music.deezer_id == track["deezer_id"])

        if track_object.youtube_id is None:
            track_object.youtube_id = youtube.get_youtube_id(track["artist"], track["title"])
            track_object.save()

        track["youtube_id"] = track_object.youtube_id

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
    for position, track in enumerate(general_chart, 1):
        track["position"] = position

    with open(f'static/general_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(general_chart, f)

    return general_chart


def get_general_chart():
    yandex_chart = yandex.get_chart_info()
    yandex_chart = update_yandex_chart(yandex_chart)

    deezer_chart = deezer.get_chart_info()
    deezer_chart = update_deezer_chart(deezer_chart)

    general_chart = calc_general_chart(yandex_chart, deezer_chart)

    return general_chart
