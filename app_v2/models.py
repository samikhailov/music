from peewee import *


db = SqliteDatabase("db.sqlite3")


class GlobalTrack(Model):
    id = AutoField()
    title = CharField()
    artist = CharField()
    deezer_id = IntegerField(null=True, unique=True)
    shazam_id = IntegerField(null=True, unique=True)
    spotify_id = CharField(null=True, unique=True)
    youtube_id = CharField(null=True, unique=True)
    chorus_start = TimeField(null=True)

    class Meta:
        database = db
        constraints = [SQL("CONSTRAINT track UNIQUE (artist, title)")]
        legacy_table_names=False
