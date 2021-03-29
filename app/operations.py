import logging
from typing import Union, List
from dataclasses import dataclass, field
from app import deezer, shazam, spotify, yandex, youtube
from app.models import Track, BaseTrack


@dataclass
class Chart:
    service: Union["yandex", "deezer", "shazam", "spotify", "internal"]
    tracks: List[Union[Track, BaseTrack]] = field(default_factory=list)
    
    def get_chart(self):
        if self.service == "yandex":
            self.tracks = yandex.get_chart()
        elif self.service == "deezer":
            self.tracks = deezer.get_chart()
        elif self.service == "shazam":
            self.tracks = shazam.get_chart()
        elif self.service == "spotify":
            self.tracks = spotify.get_chart()
        elif self.service == "internal":
            pass
        return self


def create_internat_chart(chart_lenght=50):
    # TODO: Сделать что-то нормальное.
    deezer_chart = Chart("deezer").get_chart()
    yandex_chart = Chart("yandex").get_chart()
    shazam_chart = Chart("shazam").get_chart()
    spotify_chart = Chart("spotify").get_chart()

    charts = [yandex_chart, deezer_chart, shazam_chart, spotify_chart]
    internal_chart_tmp = {}
    for chart in charts:
        for base_track in chart.tracks:
            track = base_track.get_track()
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
