import json
from tasks import yandex, youtube, deezer, shazam
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
        track["deezer_id"] = deezer.get_track_id(track["artist"], track["title"])
        track["shazam_id"] = shazam.get_track_id(track["artist"], track["title"])
    elif service == "deezer":
        track["yandex_id"] = yandex.get_track_id(track["artist"], track["title"])
        track["shazam_id"] = shazam.get_track_id(track["artist"], track["title"])
    elif service == "shazam":
        track["yandex_id"] = yandex.get_track_id(track["artist"], track["title"])
        track["deezer_id"] = deezer.get_track_id(track["artist"], track["title"])
    else:
        return None

    track_object = Music.create(
        artist=track["artist"],
        title=track["title"],
        yandex_id=track["yandex_id"],
        deezer_id=track["deezer_id"],
        shazam_id=track["shazam_id"]
    )

    return track_object


def update_yandex_chart(yandex_chart):
    """
    Добавление id других сервисов в yandex_chart
    """
    for track in yandex_chart:
        track_object = Music.get_or_none(Music.yandex_id == track["yandex_id"])
        if track_object is None:
            track_object = insert_track(track, "yandex")
        track["deezer_id"] = track_object.deezer_id
        track["shazam_id"] = track_object.shazam_id

    with open(f'static/yandex_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(yandex_chart, f)

    return yandex_chart


def update_deezer_chart(deezer_chart):
    """
    Добавление id других сервисов в deezer_chart
    """
    for track in deezer_chart:
        track_object = Music.get_or_none(Music.deezer_id == track["deezer_id"])
        if track_object is None:
            track_object = insert_track(track, "deezer")
        track["yandex_id"] = track_object.yandex_id
        track["shazam_id"] = track_object.shazam_id

    with open(f'static/deezer_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(deezer_chart, f)

    return deezer_chart


def update_shazam_chart(shazam_chart):
    """
    Добавление id других сервисов в shazam_chart
    """
    for track in shazam_chart:
        track_object = Music.get_or_none(Music.shazam_id == track["shazam_id"])
        if track_object is None:
            track_object = insert_track(track, "shazam")
        track["yandex_id"] = track_object.yandex_id
        track["deezer_id"] = track_object.deezer_id

    with open(f'static/shazam_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(shazam_chart, f)

    return shazam_chart


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


def calc_general_chart(yandex_chart, deezer_chart, shazam_chart):
    """
    Расчет глобального чата
    """
    # За основу взят чарт Яндекса
    general_chart = yandex_chart.copy()

    # Добавление в глобальный чарт Deezer
    for deezer_track in deezer_chart:
        for general_track in general_chart:
            if general_track["deezer_id"] == deezer_track["deezer_id"]:
                general_track["point"] += deezer_track["point"]
                break
        else:
            general_chart.append(deezer_track)

    # Добавление в глобальный чат Shazam
    for shazam_track in shazam_chart:
        for general_track in general_chart:
            if general_track["deezer_id"] == shazam_track["deezer_id"]:
                general_track["point"] += shazam_track["point"]
                break
        else:
            general_chart.append(shazam_track)

    general_chart.sort(key=lambda dictionary: dictionary['point'], reverse=True)

    for position, track in enumerate(general_chart, 1):
        track["position"] = position

    with open(f'static/general_chart {datetime.today().strftime("%y-%m-%d %H-%M-%S")}.json', 'w', encoding='utf-8') as f:
        json.dump(general_chart, f)

    return general_chart


def get_general_chart():
    yandex_chart = yandex.get_chart()
    yandex_chart = update_yandex_chart(yandex_chart)

    deezer_chart = deezer.get_chart()
    deezer_chart = update_deezer_chart(deezer_chart)

    shazam_chart = shazam.get_chart()
    shazam_chart = update_shazam_chart(shazam_chart)

    general_chart = calc_general_chart(yandex_chart, deezer_chart, shazam_chart)

    return general_chart
