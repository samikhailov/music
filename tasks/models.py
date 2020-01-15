from peewee import *


db = SqliteDatabase('music.sqlite3')


class Music(Model):
    id = IntegerField(unique=True, primary_key=True)
    artist = CharField()
    title = CharField()
    yandex_id = IntegerField(null=True, default=None)
    deezer_id = IntegerField(null=True, default=None)
    youtube_id = CharField(null=True, default=None)
    video_start = TimeField(default="00:00:00")

    class Meta:
        database = db
