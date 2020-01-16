from peewee import *


db = SqliteDatabase('music.sqlite3')


class Music(Model):
    id = IntegerField(unique=True, primary_key=True)
    artist = CharField()
    title = CharField()
    yandex_id = IntegerField(null=True, default=None, unique=True)
    deezer_id = IntegerField(null=True, default=None, unique=True)
    shazam_id = IntegerField(null=True, default=None, unique=True)
    youtube_id = CharField(null=True, default=None, unique=True)
    video_start = TimeField(null=True, default=None)

    class Meta:
        database = db
