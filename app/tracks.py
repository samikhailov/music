from logging import Logger
import os
import sys
import requests
import re
from app.utils import spotify_request, action_log, action_log_track, logging
from app.models import GlobalTrack
from settings import YOUTUBE_TOKEN


class Track:
    def __init__(self, artist, title, id=None, service=None, position=None) -> None:
        self.id = id
        self.artist = artist
        self.title = title
        self.position = position
        self.service = service

    @action_log_track
    def get_deezer_track_id(self) -> str:
        search = re.sub(r"& |Feat. ", "", f"{self.artist} {self.title}")
        url = f"https://api.deezer.com/search"
        params = {"q": search}
        data = requests.get(url, params=params).json()
        if data["total"] == 0:
            return None
        return str(data["data"][0]["id"])

    @action_log_track
    def get_shazam_track_id(self):
        query = re.sub(r"& |Feat. ", "", f"{self.artist} {self.title}")
        url = "https://www.shazam.com/services/search/v3/ru/RU/web/search"
        params = {"query": query, "numResults": "1", "offset": "0", "types": "artists,songs"}
        data = requests.get(url, params=params).json()
        if data == {}:
            return None
        return data["tracks"]["hits"][0]["key"]

    @spotify_request
    @action_log_track
    def get_spotify_track_id(self):
        query = re.sub(r"& |Feat. ", "", f"{self.artist} {self.title}")
        url = "https://api.spotify.com/v1/search"
        params = {"q": query, "type": "track", "market": "RU", "limit": "1"}
        headers = {"Authorization": f"Bearer {os.getenv('SPOTIFY_ACCESS_TOKEN')}"}
        data = requests.get(url, params=params, headers=headers).json()
        if data["tracks"]["items"] == []:
            return None
        return data["tracks"]["items"][0]["id"]

    @action_log_track
    def get_youtube_track_id(self):
        search = f"{self.artist} {self.title}"
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {"part": "snippet", "maxResults": 1, "q": search, "key": YOUTUBE_TOKEN}
        data = requests.get(url, params=params).json()

        if data.get("error"):
            logging.error(data["error"])
            sys.exit(0)
        elif data["pageInfo"]["totalResults"] == 0:
            logging.error("Video not found")
            sys.exit(0)
        else:
            return data["items"][0]["id"]["videoId"]

    def get_track_id(self, service):
        if service == "deezer":
            return self.get_deezer_track_id()
        elif service == "shazam":
            return self.get_shazam_track_id()
        elif service == "spotify":
            return self.get_spotify_track_id()
        elif service == "youtube":
            return self.get_youtube_track_id()

    @action_log_track
    def get_global_track(self) -> GlobalTrack:
        track_ids = {"deezer": "", "shazam": "", "spotify": ""}
        services = list(track_ids.keys())
        if self.service:
            index = services.index(self.service)
            services[0], services[index] = services[index], services[0]
        for service in services:
            if self.service == service:
                track_ids[service] = self.id
            else:
                track_ids[service] = self.get_track_id(service)
            global_track = GlobalTrack.get_global_track(track_ids[service], service)
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
        return f"Track('{self.artist}', '{self.title}', '{self.id}', '{self.service}', {self.position})"


class Chart:
    """
    service: global, deezer, shazam, spotify
    """

    def __init__(self, service, limit=100) -> None:
        self.service = service
        self.limit = limit
        self.tracks = self.get_chart()

    @staticmethod
    @action_log
    def get_deezer_chart(limit=100):
        url = "https://api.deezer.com/playlist/1116189381"
        params = {"index": 0, "limit": limit}
        data = requests.get(url, params=params).json()
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
    def get_shazam_chart(limit=100):
        url = "https://www.shazam.com/shazam/v2/ru/RU/web/-/tracks/country-chart-RU"
        params = {"pageSize": limit, "startFrom": "0"}
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
    def get_spotify_chart(limit=100):
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
            if position == limit:
                break
        return tracks

    @staticmethod
    @action_log
    def get_global_chart(limit=100):
        tmp_chart = {}
        for get_chart in [Chart.get_deezer_chart, Chart.get_shazam_chart, Chart.get_spotify_chart]:
            chart = get_chart()
            for track in chart:
                global_track = track.get_global_track()
                if not tmp_chart.get(global_track.id):
                    tmp_chart[global_track.id] = {"global_track": global_track, "weight": 0}
                tmp_chart[global_track.id]["weight"] += int(10000 / track.position)
        global_chart = []
        for position, i in enumerate(sorted(tmp_chart.values(), key=lambda x: x["weight"], reverse=True), 1):
            global_chart.append(
                Track(
                    id=i["global_track"].id,
                    artist=i["global_track"].artist,
                    title=i["global_track"].title,
                    service="global",
                    position=position,
                )
            )
            if position == limit:
                return global_chart
        return global_chart

    def get_chart(self):
        if self.service == "deezer":
            return self.get_deezer_chart(self.limit)
        elif self.service == "shazam":
            return self.get_shazam_chart(self.limit)
        elif self.service == "spotify":
            return self.get_spotify_chart(self.limit)
        elif self.service == "global":
            return self.get_global_chart(self.limit)

