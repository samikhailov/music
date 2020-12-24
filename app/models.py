from dataclasses import dataclass
import logging
from peewee import *
from app import deezer, shazam, spotify, yandex

db = SqliteDatabase("db.sqlite3")


class Track(Model):
    id = AutoField()
    title = CharField()
    artist = CharField()
    in_deezer_id = IntegerField(null=True, unique=True)
    in_shazam_id = IntegerField(null=True, unique=True)
    in_spotify_id = CharField(null=True, unique=True)
    in_yandex_id = IntegerField(null=True, unique=True)
    in_youtube_id = CharField(null=True, unique=True)
    chorus_start = TimeField(null=True)
    position = None

    class Meta:
        database = db
        constraints = [SQL("CONSTRAINT track UNIQUE (artist, title)")]

    @staticmethod
    def get_in_service_id_field(service):
        in_service_id_fields = {
            "yandex": "in_yandex_id",
            "deezer": "in_deezer_id",
            "shazam": "in_shazam_id",
            "spotify": "in_spotify_id",
        }
        return in_service_id_fields[service]


@dataclass
class BaseTrack:
    in_service_id: int
    artist: str
    title: str
    position: int
    service: str

    def create_track(self):
        logger = logging.getLogger('app.models.BaseTrack.create_track')
        in_service_id_field = Track.get_in_service_id_field(self.service)
        kwargs = {
            "title": self.title,
            "artist": self.artist,
            in_service_id_field: self.in_service_id,
        }
        track = Track.create(**kwargs)
        logger.info(f"Track recorded in DB - {track}")
        return track


    def get_track_by_same_service(self):
        logger = logging.getLogger('app.models.BaseTrack.get_track_by_same_service')
        in_service_id_field = Track.get_in_service_id_field(self.service)
        track = Track.get_or_none(getattr(Track, in_service_id_field) == self.in_service_id)
        if track:
            logger.info(f"Track found in DB - {self}")
            return track
        else:
            logger.info(f"Track not found in DB - {self}")
            

    def get_track_by_another_service(self, service):
        logger = logging.getLogger('app.models.BaseTrack.get_track_by_another_service')
        """
        Возвращает None, если значения сервиса в треке и в параметре метода совпадают.
        """
        if service == self.service:
            return None

        if service == "deezer":
            in_service_id = deezer.get_track_id(self.artist, self.title)
        elif service == "shazam":
            in_service_id = shazam.get_track_id(self.artist, self.title)
        elif service == "spotify":
            in_service_id = spotify.get_track_id(self.artist, self.title)
        elif service == "yandex":
            in_service_id = yandex.get_track_id(self.artist, self.title)
        else:
            raise ValueError(f"Service '{service}' not supported.")

        if in_service_id:
            in_service_id_field = Track.get_in_service_id_field(service)
            track = Track.get_or_none(getattr(Track, in_service_id_field) == in_service_id)
        else:
            return None

        if track:
            setattr(track, in_service_id_field, self.in_service_id)
            track.save()
            logger.info(f"Track updated in DB (field: {in_service_id_field}, {track})")
            return track

    def get_track(self):
        logger = logging.getLogger('app.models.BaseTrack.get_track')
        track = (
            self.get_track_by_same_service()
            or self.get_track_by_another_service("deezer")
            or self.get_track_by_another_service("shazam")
            or self.get_track_by_another_service("spotify")
            or self.get_track_by_another_service("yandex")
            or self.create_track()
        )
        return track


"""
from app.models import *
bt = BaseTrack(in_service_id=59688561, artist='клава кока', title='мне пох', position=10, service='yandex')

t = bt.get_track_by_another_service('shazam')

"""
