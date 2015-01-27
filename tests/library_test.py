from __future__ import unicode_literals
import datetime
import sys
sys.path.append('../mopidy_remote')
from library import RemoteLibrary
import musicbrainzngs

config = {}
config['remote'] = {}
config['remote']['database'] = '/var/lib/mopidy/remote.db'


lib = RemoteplayLibrary(config)
musicbrainzngs.set_useragent('mopidy-headless','0.0.1')
result = musicbrainzngs.search_releases(release="Dandy in the Underworld",artist="T. Rex")

import pdb; pdb.set_trace()
res =  musicbrainzngs.search_artists(artist='T. Rex')
[(art['name'],art['ext:score']) for art in result['artist-list'] if int(art['ext:score']) > 30]

result = musicbrainzngs.search_recordings(recording="Crimson Moon", release="Dandy in the Underworld",artist="T. Rex")
track = [t for t in result['recording-list'] if int(t['ext:score']) == 100][0]
musicbrainz_id = track['id']

rec = musicbrainzngs.get_recording_by_id('9abfbf0b-ef05-4dfc-9177-17cc42dd3feb',includes=['artists','releases'])
track = rec['recording']
album = track['release-list'][0]['title']
artist = track['artist-credit-phrase']
