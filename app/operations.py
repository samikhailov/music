import logging
from app import deezer, shazam, spotify, yandex, youtube
from app.models import Track, BaseTrack


def get_track_obj(base_track):
    # TODO: Вынести дублирующийся код в отдельную функцию.
    service_mapping = {
        "yandex": "in_yandex_id",
        "deezer": "in_deezer_id",
        "shazam": "in_shazam_id",
        "spotify": "in_spotify_id",
    }
    in_service_id_field = service_mapping[base_track.service]

    # Поиск трека по ID того же сервиса внутри БД.
    track = Track.get_or_none(getattr(Track, in_service_id_field) == base_track.in_service_id)
    if track:
        logging.info(f"Track found in DB ({track.id}, {track.artist}, {track.title})")
        return track

    # Поиск трека сервиса по ID стороннего сервиса и обновление или создание записи в базе.
    # Deezer
    in_deezer_id = None
    if base_track.service != "deezer":
        in_deezer_id = deezer.get_track_id(base_track.artist, base_track.title)
        if in_deezer_id:
            track = Track.get_or_none(Track.in_deezer_id == in_deezer_id)
        if track:
            setattr(track, in_service_id_field, base_track.in_service_id)
            track.save()
            logging.info(
                f"Track updated in DB ({in_service_id_field}={base_track.in_service_id}, {track.id}, {track.artist}, "
                f"{track.title})"
            )
            return track
    # Shazam
    in_shazam_id = None
    if base_track.service != "shazam":
        in_shazam_id = shazam.get_track_id(base_track.artist, base_track.title)
        if in_shazam_id:
            track = Track.get_or_none(Track.in_shazam_id == in_shazam_id)
        if track:
            setattr(track, in_service_id_field, base_track.in_service_id)
            track.save()
            logging.info(
                f"Track updated in DB ({in_service_id_field}={base_track.in_service_id}, {track.id}, {track.artist}, "
                f"{track.title})"
            )
            return track
    # Spotify
    in_spotify_id = None
    if base_track.service != "spotify":
        in_spotify_id = spotify.get_track_id(base_track.artist, base_track.title)
        if in_spotify_id:
            track = Track.get_or_none(Track.in_spotify_id == in_spotify_id)
        if track:
            setattr(track, in_service_id_field, base_track.in_service_id)
            track.save()
            logging.info(
                f"Track updated in DB ({in_service_id_field}={base_track.in_service_id}, {track.id}, {track.artist}, "
                f"{track.title})"
            )
            return track
    # Yandex
    in_yandex_id = None
    if base_track.service != "yandex":
        in_yandex_id = yandex.get_track_id(base_track.artist, base_track.title)
        if in_yandex_id:
            track = Track.get_or_none(Track.in_yandex_id == in_yandex_id)
        if track:
            setattr(track, in_service_id_field, base_track.in_service_id)
            track.save()
            logging.info(
                f"Track updated in DB ({in_service_id_field}={base_track.in_service_id}, {track.id}, {track.artist}, "
                f"{track.title})"
            )
            return track

    kwargs = {
        "artist": base_track.artist,
        "title": base_track.title,
        "in_deezer_id": in_deezer_id,
        "in_yandex_id": in_yandex_id,
        in_service_id_field: base_track.in_service_id,
    }
    track = Track.create(**kwargs)
    logging.info(f"New track recorded in DB ({track.id}, {track.artist}, {track.title})")
    logging.debug(kwargs)
    return track


def create_internat_chart(chart_lenght=50):
    # TODO: Сделать что-то нормальное.
    yandex_chart = yandex.get_chart()
    deezer_chart = deezer.get_chart()
    shazam_chart = shazam.get_chart()
    spotify.put_access_token_to_env()
    spotify_chart = spotify.get_chart()

    charts = [yandex_chart, deezer_chart, shazam_chart, spotify_chart]
    internal_chart_tmp = {}
    for chart in charts:
        for base_track in chart:
            track = get_track_obj(base_track)
            if internal_chart_tmp.get(track.id) is None:
                internal_chart_tmp[track.id] = {"track": track, "weight": int(10000 / base_track.position)}
            else:
                internal_chart_tmp[track.id]["weight"] += int(10000 / base_track.position)
    internal_chart_tmp = sorted(internal_chart_tmp.items(), key=lambda x: x[1]["weight"], reverse=True)
    tracks = []
    for position, track in enumerate(internal_chart_tmp, 1):
        kwargs = track[1]["track"].__dict__
        kwargs["position"] = position
        tracks.append(Track(**kwargs))
        if position == chart_lenght:
            break
    logging.info(f"Internal chart created (chart_lenght={chart_lenght})")
    return tracks


def update_in_youtube_ids(chart):
    for track in chart:
        if track.in_youtube_id:
            logging.info(
                f"Track found in DB (in_youtube_id={track.in_youtube_id}, {track.id}, {track.artist}, "
                f"{track.title})"
            )
        else:
            track.in_youtube_id = youtube.get_video_id(track.artist, track.title)
            track.save()
            logging.info(
                f"Track updated in DB (in_youtube_id={track.in_youtube_id}, {track.id}, {track.artist}, "
                f"{track.title})"
            )
    return chart
