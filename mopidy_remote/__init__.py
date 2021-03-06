from __future__ import unicode_literals

import logging
import os

# TODO: Remove entirely if you don't register GStreamer elements below
#import pygst
#pygst.require('0.10')
#import gst
#import gobject

from mopidy import config, ext


__version__ = '0.0.1'

# TODO: If you need to log, use loggers named after the current Python module
logger = logging.getLogger(__name__)


class Extension(ext.Extension):

    dist_name = 'Mopidy-Remote'
    ext_name = 'remote'
    version = __version__

    def get_default_config(self):
        conf_file = os.path.join(os.path.dirname(__file__), 'ext.conf')
        return config.read(conf_file)

    def get_config_schema(self):
        schema = super(Extension, self).get_config_schema()
        schema['set_consume'] = config.Boolean(optional=True)
        schema['get_tracks'] = config.Integer(optional=True)
        schema['get_albums'] = config.Integer(optional=True)
        schema['find_exact'] = config.Boolean(optional=True)
        schema['database'] = config.String(optional=True)
        schema['lastfm_username'] = config.String()
        schema['lastfm_password'] = config.String()
        return schema

    def setup(self, registry):
        from .frontend import factory
        from .listener import RemoteListener
        registry.add('http:app', {'name': 'remote', 'factory': factory})	
        registry.add('frontend', RemoteListener)
