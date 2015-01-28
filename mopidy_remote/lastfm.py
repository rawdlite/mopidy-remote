from __future__ import unicode_literals

import logging
import pylast

API_KEY = '56e851239917399f79ed0e97e6431894'
API_SECRET = '081714a14e0bf3e3517b256f281ad437'

logger = logging.getLogger(__name__)

class LastFM():
    def __init__(self,config):
        self.config = config
        self.lastfm = None
        try:
            self.lastfm = pylast.LastFMNetwork(
                api_key=API_KEY, api_secret=API_SECRET,
                username=self.config['remote']['lastfm_username'],
                password_hash=pylast.md5(self.config['remote']['lastfm_password']))
            logger.info('Scrobbler connected to Last.fm')
        except (pylast.NetworkError, pylast.MalformedResponseError,
                pylast.WSError) as e:
            logger.error('Error during Last.fm setup: %s', e)


    def get_related_artists(self,artist, discriminator=0.5):
        # import pdb; pdb.set_trace()
        artist = self.lastfm.get_artist(artist)
        artists = artist.get_similar()
        return [{'name': a.item.name, 
                 'playcount': a.item.get_userplaycount(),
                 'match': a.match} for a in artists if a.match > discriminator]
        # get_artist_by_mbid

    def get_genre(self,item):
        """ use folksonomy tags as genre """
        # import pdb; pdb.set_trace()
        if isinstance(item) == Artist:
            artist = self.lastfm.get_artist(artist)
            
