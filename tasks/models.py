from peewee import *


db = SqliteDatabase('music.sqlite3')


class Music(Model):
    id = IntegerField(unique=True, primary_key=True)
    artist = CharField()
    title = CharField()
    yandex_id = IntegerField(null=True, default=None)
    deezer_id = IntegerField(null=True, default=None)
    shazam_id = IntegerField(null=True, default=None)
    youtube_id = CharField(null=True, default=None)
    video_start = TimeField(null=True, default=None)

    class Meta:
        database = db
