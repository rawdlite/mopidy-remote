from __future__ import unicode_literals
import peewee
from peewee import *
import datetime

db = SqliteDatabase(None)

class RemoteLibrary():

    def __init__(self, config):
        db.init(config['remote']['database'])
        db.create_tables([self.Track,self.State], safe=True)
        self.db = db

    def get_or_create_track(self, track):
        try:
            with self.db.transaction():
                return self.Track.create(title = track.name,
                                         uri = track.uri,
                                         #musicbrainz_id=track.musicbrainz_id,
                                         created_at = datetime.datetime.now())
        except peewee.IntegrityError:
            # `uri` is a unique column, so this track already exists,
            # making it safe to call .get().
            return self.Track.get(self.Track.uri == track.uri)

    def get_or_create_state(self, state):
        try:
            with self.db.transaction():
                return self.State.create(key = state)
        except peewee.IntegrityError:
            # `uri` is a unique column, so this track already exists,
            # making it safe to call .get().
            return self.State.get(self.State.key == state)

    def increase_playcount(self, track):
        library_track = self.get_or_create_track(track)
        library_track.playcount += 1
        library_track.played_last = datetime.datetime.now()
        library_track.save()
        return library_track

    def decrease_playcount(self, track):
        library_track = self.get_or_create_track(track)
        library_track.playcount -= 1
        library_track.save()
        return library_track

    def get_last_played_track(self):
        last_tracks = [i for i in self.Track.select().order_by(self.Track.played_last.desc()).limit(1)]
        return last_tracks[0]

    def set_state(self, state, value):
        status = self.get_or_create_state(state)
        status.value = value
        status.save()

    def get_state(self, state):
        try:
            status = self.State.get(self.State.key == state).value
            if status == u'1' or status == u'0' or status == u'':
                status = int(status)
        except:
            status = 0
        return status

    def toggle_state(self, state):
        status = self.get_state(state)
        status = str(int(not status))
        self.set_state(state, status)
        logger.info("%s Status: %s" % (state,status))
        return status

    class LibraryBaseModel(Model):
        class Meta:
            database = db

    class Track(LibraryBaseModel):
        title = CharField(null=True)
        uri = CharField(unique=True)
        # musicbrainz_id = CharField(null=True)
        playcount = IntegerField(null=True, default=0)
        played_last = DateField(null=True)
        skipcount = IntegerField(null=True, default=0)
        skiped_length = FloatField(null=True)
        rating = IntegerField(null=True)
        in_tracklist = BooleanField(null=True, default=False)
        created_at = DateField(null=True)
        updated_at = DateField(null=True)

    class State(LibraryBaseModel):
        key = CharField(unique=True)
        value = CharField(null=True)
