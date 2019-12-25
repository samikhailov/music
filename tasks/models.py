from peewee import *


db = SqliteDatabase('music.sqlite3')


class Track(Model):
    artist = CharField()
    title = CharField()

    class Meta:
        database = db
        indexes = (
            (('artist', 'title'), True),
        )


class Yandex(Model):
    in_service_id = IntegerField(null=True, default=None)
    track = ForeignKeyField(Track, backref='tracks')
    artist = CharField()
    title = CharField()

    class Meta:
        database = db
        indexes = (
            (('artist', 'title'), True),
        )


class Deezer(Model):
    in_service_id = IntegerField(null=True, default=None)
    track = ForeignKeyField(Track, backref='tracks')
    artist = CharField()
    title = CharField()

    class Meta:
        database = db
        indexes = (
            (('artist', 'title'), True),
        )


class Youtube(Model):
    id = CharField(unique=True, primary_key=True)
    track = ForeignKeyField(Track, backref='tracks')
    title = CharField()
    best_part_start = TimeField(default="00:00:00")

    class Meta:
        database = db
