from __future__ import unicode_literals
import ast
import os
import json
import random
import tornado.web
from mopidy import ext
from mopidy.audio import constants
import logging
from .track_info import TrackInfo
from .library import RemoteLibrary
from .lastfm import LastFM
from time import sleep

logger = logging.getLogger(__name__)

class Remote:
    def __init__(self, core, config):
        self.core = core
        self.playback = core.playback
        self.track_info = TrackInfo(config)
        self.library = RemoteLibrary(config)
        self.lastfm = LastFM(config)
        self.config = config
        self.set_consume = config['remote']['set_consume']
        self.album_option = config['remote']['get_albums']
        self.track_option = config['remote']['get_albums']
        self.exact_option = config['remote']['find_exact']
        self.database = config['remote']['database']
        logger.debug("remote initialized %s" % __name__)

    def _play_request(self, args):
        query = None
        uris = None
        options = None
        tracks = []
        albums = []
        tracks_selected = []
        albums_selected = []
        if 'query' in args:
            query = args['query']
        if 'uris' in args:
            uris = args['uris']
        if 'options' in args:
            options = args['options']
            if 'album' in options:
                self.album_option = int(options['album'])
            if 'track' in options:
                self.track_option = int(options['track'])
            if 'exact' in options:
                self.exact_option = int(options['exact'])
        logger.info("Query %s, uris = %s, options = %s" % (query,uris,options))
        if self.exact_option:
            res = self.core.library.find_exact(query, uris=uris).get()
        else:
            res = self.core.library.search(query, uris=uris).get()
        for resultset in res:
            logger.debug("Found %s tracks uri %s" % (len(resultset.tracks),resultset.uri))
            logger.debug("Found %s albums uri %s" % (len(resultset.albums),resultset.uri))
            tracks.extend(resultset.tracks)
            albums.extend(resultset.albums)
        logger.info("Found %s albums and %s tracks" % (len(albums), len(tracks)))
        if self.album_option and albums:
            albums_selected = [self._get_random_item(albums) for i in range(self.album_option)]
        if self.track_option and tracks:
            tracks_selected = [self._get_random_item(tracks) for i in range(self.track_option)]
        if self.set_consume:
            self.consume()
        if not self.is_playing() and self.has_tracks():
                self.core.tracklist.clear()
        if tracks_selected:
            [self.core.tracklist.add(uri = track.uri) for track in tracks_selected]
        if albums_selected:
            [self.core.tracklist.add(uri = album.uri) for album in albums_selected]
        # import pdb; pdb.set_trace()
        if self.core.tracklist.length.get() == 0:
            return {'tracks': None, 'albums': None}
        else:
            self.play() 
            return {'tracks': tracks_selected, 'albums': albums_selected}

    
    def _get_random_item(self, items):
        i = random.randint(0, len(items) - 1)
        item = items[i]
        logger.info("Found %s item %s" % (len(items),item.uri))
        logger.debug(item)
        return item


    def _speak_text(self,text):
        current_track = self.playback.current_track.get()
        if current_track:
            pos = self.playback.get_time_position().get()
            self.playback.stop()
        self.track_info.speak_text(text)
        if current_track:
            self.playback.pause()
            self.playback.seek(pos)
        else:
            self.play()


    def consume(self, arg=None):
        self.core.tracklist.set_consume(True)
        logger.debug("Consume %s" % self.core.tracklist.consume.get())


    def set_debugger(self, arg=None):
        status = self.library.set_state("debugger", arg)
        self._speak_text("Debugger is on %s" % arg)


    def toggle_continous(self, arg=None):
        status = self.library.toggle_state("continous")
        if status:
            self._speak_text("Continous play Status is on")
        else:
            self._speak_text("Continous play Status is off")


    def has_tracks(self, arg=None):
        tl_tracks = self.core.tracklist.tl_tracks.get()
        return tl_tracks


    def is_playing(self, arg=None):
        state = self.playback.state.get()
        logger.info("state %s %s" % (state,constants.PlaybackState.PLAYING))
        return (state == constants.PlaybackState.PLAYING)


    def play(self, arg=None):
        if not self.is_playing():
            if not self.core.tracklist.length.get():
                last_track = self.library.get_last_played_track()
                self.core.tracklist.add(uri = last_track.uri)
            self.playback.play()


    def pause(self, arg=None):
        if self.is_playing():
            self.playback.pause()
            return
        else:
            self.playback.resume()


    def stop(self, arg=None):
        self.playback.stop()


    def next(self, arg=None):
        self.playback.next()


    def previous(self, arg=None):
        self.playback.previous()


    def info(self, arg=None):
        if self.library.get_state('debugger') == u'info':
            import pdb; pdb.set_trace()
        current_track = self.get_current_track()
        text = (" You are listening to  %s by %s on %s" %
                (current_track.name,
                 " ".join([artist.name for artist in current_track.artists]),
                 current_track.album.name)).encode('ascii', 'ignore')
        logger.info(text)
        self._speak_text(text)


    def get_current_track(self, arg=None):
        current_track = None
        if not self.is_playing():
            last_track = self.library.get_last_played_track()
            current_track = self.core.library.lookup(last_track.uri).get()[0]
        else:
            current_track = self.playback.current_track.get()
        return current_track


    def related_artist(self, arg=None):
        """ Play a related artist """ 
        logger.debug("related artist called")
        current_track = self.get_current_track()
        artist_name = [artist.name for artist in current_track.artists][0]
        # Using only the first artist for now
        if '&' in artist_name:
            artist_name = artist_name.split('&')[0].strip()
        related_artists = self.lastfm.get_related_artists(artist_name)
        related_artist = related_artists[random.randint(0, len(related_artists) - 1)]
        self._speak_text("Looking for related artist %s" % related_artist['name'])
        res = self._play_request({'query': {'artist': [related_artist['name']]},
                                  'options': {'track': 0, 'album': 1, 'exact': 1}})
        if not res:
            related_artists = self.lastfm.get_related_artists(artist_name,0.5)
            related_artist = related_artists[random.randint(0, len(related_artists) - 1)]
            self._play_request({'query': {'artist': [related_artist['name']]},
                                'options': {'track': 1}})
        
        
    def more_of_album(self, arg=None):
        """ Play complete album for current track """
        current_track = self.get_current_track()
        self._play_request({'query': {'artist': [artist.name for artist in current_track.album.artists],
                                      'album':  [current_track.album.name]},
                            'options': {'track': 0, 'album': 1, 'exact': 1}})


    def more_of_artist(self, arg=None):
        """ Play another album for artist of current track """
        current_track = self.get_current_track()
        logger.info("Current Track %s" % current_track.name)
        logger.debug(current_track.artists)
        self._play_request({'query': {'artist': [artist.name for artist in current_track.artists]},
                            'options': {'track': 0, 'album': 1, 'exact': 1}})

    def more_of_genre(self, arg=None):
        """ Play album of the same genre as the current track """
        current_track = self.get_current_track()
        if current_track.genre:
            logger.info("Current Track %s" % current_track.genre)
            self._play_request({'query': {'genre': [current_track.genre]},
                                'options': {'track': 0,'album': 1}})
        else:
            self.related_artist()

class RemoteHandler(tornado.web.RequestHandler):

    def initialize(self, core, config):
        self.core = core
        self.player = Remote(self.core, config)
        self.library = RemoteLibrary(config)
        logger.debug("remote handler initialized %s" % __name__)

    def get(self):
	debugger_state = self.library.get_state('debugger')
	logger.debug("Debugger state = %s" % debugger_state)
        if debugger_state == u'get':
            import pdb; pdb.set_trace()
        cmd = self.get_argument('cmd')
        arg = self.get_argument('arg',default=None)
        if arg:
            logger.info("Arg passed: %s" % arg)
        try:
            result = getattr(self.player, cmd)(arg)
        except:
            self.write(
                'Command failed %s! This is Mopidy %s' %
                (cmd, self.core.get_version().get()))
        self.finish()

    def post(self):
        debugger_state = self.library.get_state('debugger')
	logger.debug("Debugger state = %s" % debugger_state)
        if debugger_state == u'post':
             import pdb; pdb.set_trace()
        data = self.request.body
        payload = ast.literal_eval(data.decode("utf-8"))
        # payload = json.loads(data)
        res = self.player._play_request(payload)
        if res['tracks'] or res['albums']:
            [self.write("Chosen Track %s by %s on %s from %s \n" % (
                track.name,
                ",".join([a.name for a in track.album.artists]),
                track.album.name,
                track.date)) for track in res['tracks']]
            [self.write("Album %s by %s from %s \n" % (
                album.name,
                ",".join([a.name for a in album.artists]),
                album.date)) for album in res['albums']]
        else:
            self.write("No Track found, sorry")
        self.finish()

def factory(config, core):
    logger.debug("remote_factory initialized")
    return [
        ('/', RemoteHandler, {'core': core, 'config': config})
    ]

