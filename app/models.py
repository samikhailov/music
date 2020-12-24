from peewee import *


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


class BaseTrack:
    def __init__(self, in_service_id: int, title: str, artist: str, position: int, service: str):
        self.in_service_id = in_service_id
        self.artist = artist
        self.title = title
        self.position = position
        self.service = service

    def __repr__(self):
        return f"Track({self.in_service_id}, {self.artist}, {self.title}, {self.position}, {self.service})"
