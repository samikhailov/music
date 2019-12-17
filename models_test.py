from peewee import *
import json
from hashlib import md5


db = SqliteDatabase('music9.db')


class Track(Model):
    id = CharField(unique=True, primary_key=True)
    artist = CharField()
    title = CharField()

    class Meta:
        database = db
        indexes = (
            (('artist', 'title'), True),
        )


class Yandex(Model):
    id = CharField(unique=True, primary_key=True)
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
    id = CharField(unique=True, primary_key=True)
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


db.create_tables([Track, Yandex, Deezer, Youtube])
db.drop_tables([Track, Yandex, Deezer, Youtube])

artist = "Beats"
title = "Merry Christmas Trap"
name_hash = hash(f'{artist} - {title}')
Track.create(artist=artist, title=title, name_hash=name_hash)

artist = "GAYAZOV$ BROTHER$"
title = "Увезите меня на Дип-хаус"
name_hash = hash(f'{artist} - {title}')
Track.create(artist="GAYAZOV$ BROTHER$", title="Увезите меня на Дип-хаус", name_hash=name_hash)

a = Track.select().where(Track.name_hash == 6040737065790746235).get()

with open("D:/Documents/Code/music/static/music_base.json") as f:
    base = json.load(f)


o = md5('hello'.encode('utf-8'))

o.hexdigest()
a = '5d41402abc4b2a76b9719d911017c592'


Youtube.create(id=i["youtube_id"], track=i["id"], title=f'{i["artist"]} - {i["title"]}')

a = {
    "artist": "Rx Beats",
    "title": "Merry Christmas Trap",
    "youtube_id": "",
    "yandex_id": 59053630,
    "deezer_id": 779828522,
    "video_start": "00:00:00",
    "id": "76ffe0e014adc0cf6e7ddafb69c7a846"
},


class Youtube(Model):
    id = CharField(unique=True, primary_key=True)
    track = ForeignKeyField(Track, backref='tracks')
    title = CharField()
    best_part_start = TimeField(default="00:00:00")
