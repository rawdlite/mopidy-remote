import logging

import pykka
from mopidy.core import CoreListener
from .library import RemoteLibrary
from .frontend import Remote

logger = logging.getLogger(__name__)

class RemoteListener(pykka.ThreadingActor, CoreListener):

    def __init__(self, config, core):
        super(RemoteListener, self).__init__()
        self.core = core
        self.config = config
        self.player = Remote(core,config)
        self.library = RemoteLibrary(config)
        logger.info("Listener initialized")

    def on_stop(self):
        logger.info("Remote stopped")

    def tracklist_changed(self):
        logger.info("Tracklist changed")
        length = int(self.core.tracklist.length.get())
        logger.info("Have %s Tracks in Playlist" % (remaining))

    def playback_state_changed(self, old_state, new_state):
        logger.info("Playback changed from %s to %s" % (old_state, new_state))
        

    def track_playback_started(self, tl_track):
        (tlid, track) = tl_track
        if self.library.get_state('debugger') == u'track_playback_started':
            import pdb; pdb.set_trace()
        artists = ', '.join(sorted([a.name for a in track.artists]))
        logger.info('Now playing track: %s - %s', artists, track.name)
        tl_length = self.core.tracklist.length.get()
        tl_index = self.core.tracklist.index(tl_track).get()
        tl_remaining = tl_length - tl_index
        logger.info("Tracklist remaining %s index: %s ltid: %s length %s" % (tl_remaining,tl_index,tlid,tl_length))
        if tl_remaining < 2 and int(self.library.get_state("continous")):
            self.player.related_artist()
        

    def track_playback_ended(self, tl_track, time_position):
        (tlid, track) = tl_track
        if self.library.get_state('debugger') == u'track_playback_ended':
            import pdb; pdb.set_trace()
        logger.info("Track %s at tlid %s changed at position %s" % (track.name, tlid, time_position))
        logger.debug(track)
        duration = track.length and track.length // 1000 or 0
        time_position = time_position // 1000
        if time_position < duration:
            logger.info("Track skipped at %s" % (time_position / duration))
        else:
            lib_track = self.library.increase_playcount(track)
            logger.info("Track: %s Playcount: %s" % (lib_track.title,lib_track.playcount))
        
        
