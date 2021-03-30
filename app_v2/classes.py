import os
import requests
import re
from app_v2.utils import spotify_request, action_log
from app_v2.models import GlobalTrack


class Track:
    def __init__(self, artist, title, service, id, position) -> None:
        self.id = id
        self.artist = artist
        self.title = title
        self.position = position
        self.service = service

    @action_log
    def get_deezer_track_id(self) -> str:
        search = re.sub(r"& |Feat. ", "", f"{self.artist} {self.title}")
        url = f"https://api.deezer.com/search"
        params = {"q": search}
        data = requests.get(url, params=params).json()
        if data["total"] == 0:
            return None
        return str(data["data"][0]["id"])

    @action_log
    def get_shazam_track_id(self) -> str:
        url = "https://www.shazam.com/services/search/v3/ru/RU/web/search"
        params = {"query": f"{self.artist} {self.title}", "numResults": "1", "offset": "0", "types": "artists,songs"}
        data = requests.get(url, params=params).json()
        if data == {}:
            return None
        return data["tracks"]["hits"][0]["key"]

    @spotify_request
    @action_log
    def get_spotify_track_id(self) -> str:
        url = "https://api.spotify.com/v1/search"
        params = {"q": f"{self.artist} {self.title}", "type": "track", "market": "RU", "limit": "1"}
        headers = {"Authorization": f"Bearer {os.getenv('SPOTIFY_ACCESS_TOKEN')}"}
        data = requests.get(url, params=params, headers=headers).json()
        if data["tracks"]["items"] == []:
            return None
        return data["tracks"]["items"][0]["id"]

    def get_track_id(self, service) -> str:
        if service == "deezer":
            return self.get_deezer_track_id()
        elif service == "shazam":
            return self.get_shazam_track_id()
        elif service == "spotify":
            return self.get_spotify_track_id()

    @action_log
    def get_global_track(self):
        service_id_fields = {
            "deezer": GlobalTrack.deezer_id,
            "shazam": GlobalTrack.shazam_id,
            "spotify": GlobalTrack.spotify_id,
        }
        track_ids = {"deezer": "", "shazam": "", "spotify": ""}
        services = list(track_ids.keys())
        index = services.index(self.service)
        services[0], services[index] = services[index], services[0]
        for service in services:
            if self.service == service:
                track_ids[service] = self.id
            else:
                track_ids[service] = self.get_track_id(service)
            global_track = GlobalTrack.select().where(service_id_fields[service] == track_ids[service]).first()
            if global_track:
                break
        else:
            # TODO: handle exeption
            global_track = GlobalTrack.create(
                title=self.title,
                artist=self.artist,
                deezer_id=track_ids["deezer"],
                shazam_id=track_ids["shazam"],
                spotify_id=track_ids["spotify"],
            )
        return global_track

    def __repr__(self):
        return f"Track('{self.artist}', '{self.title}', '{self.service}', '{self.id}', {self.position})"


class Chart:
    """
    service: global, deezer, shazam, spotify
    """

    def __init__(self, service) -> None:
        self.service = service
        self.tracks = self.get_chart()

    @staticmethod
    @action_log
    def get_deezer_chart():
        url = "https://api.deezer.com/playlist/1116189381"
        data = requests.get(url).json()
        tracks = []
        for position, track in enumerate(data["tracks"]["data"], 1):
            tracks.append(
                Track(
                    id=str(track["id"]),
                    title=track["title"],
                    artist=track["artist"]["name"],
                    position=position,
                    service="deezer",
                )
            )
        return tracks

    @staticmethod
    @action_log
    def get_shazam_chart():
        url = "https://www.shazam.com/shazam/v2/ru/RU/web/-/tracks/country-chart-RU"
        params = {"pageSize": "100", "startFrom": "0"}
        data = requests.get(url, params=params).json()
        tracks = []
        for position, track in enumerate(data["chart"], 1):
            tracks.append(
                Track(
                    id=track["key"],
                    title=track["heading"]["title"],
                    artist=track["heading"]["subtitle"],
                    position=position,
                    service="shazam",
                )
            )
        return tracks

    @staticmethod
    @spotify_request
    @action_log
    def get_spotify_chart():
        """
        Метод получения списка лучших треков Spotify.
        """
        url = "https://api.spotify.com/v1/playlists/5I4WLaJYpw1pPcRXwUQ9XV"
        params = {"market": "RU", "fields": "tracks.items(track(name,id,artists(name)))"}
        headers = {"Authorization": f"Bearer {os.getenv('SPOTIFY_ACCESS_TOKEN')}"}
        data = requests.get(url, params=params, headers=headers).json()
        tracks = []
        for position, track in enumerate(data["tracks"]["items"], 1):
            tracks.append(
                Track(
                    id=track["track"]["id"],
                    title=track["track"]["name"],
                    artist=", ".join([i["name"] for i in track["track"]["artists"]]),
                    position=position,
                    service="spotify",
                )
            )
        return tracks

    @staticmethod
    @action_log
    def get_global_chart():
        tmp_chart = {}
        for get_chart in [Chart.get_deezer_chart, Chart.get_shazam_chart, Chart.get_spotify_chart]:
            chart = get_chart()
            for track in chart:
                global_track = track.get_global_track()
                if not tmp_chart.get(global_track.id):
                    tmp_chart[global_track.id] = {"global_track": global_track, "weight": 0}
                tmp_chart[global_track.id]["weight"] += int(10000 / track.position)
        global_chart = []
        for position, i in enumerate(sorted(tmp_chart.items(), key=lambda x: x[1]["weight"], reverse=True), 1):
            global_chart.append(
                Track(
                    id=i[1]["global_track"].id,
                    artist=i[1]["global_track"].artist,
                    title=i[1]["global_track"].title,
                    service="global",
                    position=position,
                )
            )
        return global_chart

    def get_chart(self):
        if self.service == "deezer":
            return self.get_deezer_chart()
        elif self.service == "shazam":
            return self.get_shazam_chart()
        elif self.service == "spotify":
            return self.get_spotify_chart()
        elif self.service == "global":
            return self.get_global_chart()