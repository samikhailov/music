from peewee import *


db = SqliteDatabase("db.sqlite3")


class GlobalTrack(Model):
    id = AutoField()
    artist = CharField()
    title = CharField()
    deezer_id = IntegerField(null=True, unique=True)
    shazam_id = IntegerField(null=True, unique=True)
    spotify_id = CharField(null=True, unique=True)
    youtube_id = CharField(null=True, unique=True)
    chorus_start = TimeField(null=True)

    def get_global_track(id, service):
        service_id_fields = {
            "global": GlobalTrack.id,
            "deezer": GlobalTrack.deezer_id,
            "shazam": GlobalTrack.shazam_id,
            "spotify": GlobalTrack.spotify_id,
        }
        return (
            GlobalTrack.select()
            .where((service_id_fields[service] == id) & (service_id_fields[service].is_null(False)))
            .first()
        )

    def update_youtube_id(self, youtube_id):
        self.youtube_id = youtube_id
        self.save()

    def update_chorus_start(self, chorus_start):
        self.chorus_start = chorus_start
        self.save()

    class Meta:
        database = db
        constraints = [SQL("CONSTRAINT track UNIQUE (artist, title)")]
        legacy_table_names = False
