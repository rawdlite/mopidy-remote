from __future__ import unicode_literals
import logging
import urllib
from time import sleep
import gobject
import tempfile
import subprocess
import pipes
import os
import pygst
pygst.require('0.10')
import gtts
import gst

logger = logging.getLogger(__name__)
# Default flags to use for playbin: AUDIO,  DOWNLOAD
PLAYBIN_FLAGS = (1 << 1) | (1 << 7)

class TrackInfo():
    def __init__(self,config):
        self.config = config

    def _execute(self, cmd):
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                logger.debug("Output was: '%s'", output)
        

    def _play(self, filename):
        cmd = ['mplayer', '-af', 'resample=44100', '-ao', 'alsa:device=isq_digital', str(filename)]
        logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                               for arg in cmd]))
        self._execute(cmd)
        os.remove(filename)
        

                
    def speak_text(self, phrase):
        # import pdb; pdb.set_trace()
        logger.debug("Saying '%s' with '%s'", phrase, 'pico2wave')
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = ['pico2wave', '--wave', fname, '-l', 'en-GB' ]
        cmd.append(phrase)
        logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                     for arg in cmd]))
        self._execute(cmd)
        self._play(fname)

# for later reference only

    def speak_text_gtts(self, phrase):
        tts = gtts.gTTS(text=phrase, lang='en')
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            tmpfile = f.name
        tts.save(tmpfile)
        self._play(tmpfile)
        

    def gtts_stream(self, text):
        params = {}
        params['tl'] = 'en'
        params['q'] = text
        return 'http://translate.google.com/translate_tts?' \
                           + urllib.urlencode(params)


    def _speak_stream(self,stream):
        cmd = '/usr/bin/mplayer "'
        cmd += stream
        cmd += '" -af resample=44100 '
        # TODO use config
        cmd += ' -ao alsa:device=isq_digital'
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, shell=True, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                logger.debug("Output was: '%s'", output)

    def speak_text_gs(self,track):
        # import pdb; pdb.set_trace()
        self.pipeline = gst.Pipeline()
        self.playbin = gst.element_factory_make("playbin2", "tts_pipeline")
        self.playbin.set_property('flags', PLAYBIN_FLAGS)
        self.playbin.set_property('buffer-size', 2*1024*1024)
        self.playbin.set_property('buffer-duration', 2*gst.SECOND)
        
        # self.playbin.set_property('delay', 50*gst.MSECOND)
        self.pipeline.add(self.playbin)
        bin = gst.Bin("speed-bin")
        pitch = gst.element_factory_make("pitch","tts_pitch")
        pitch.set_property("tempo", 0.7)
        pitch.set_property("pitch", 0.8)
        bin.add(pitch)
        audiosink = gst.parse_bin_from_description(self.config['audio']['output'],
                                                   ghost_unconnected_pads=True)

        rate_bin = gst.parse_bin_from_description("audioresample ! audio/x-raw-int, endianness=1234, signed=true, width=32, depth=32, rate=44100, channels=2 ! audioconvert ! alsasink device=isq_digital")
        bin.add(audiosink)
        convert = gst.element_factory_make("audioconvert", "tts_convert")
        bin.add(convert)
        gst.element_link_many(pitch, convert)
        gst.element_link_many(convert, audiosink)
        sink_pad = gst.GhostPad("sink", pitch.get_pad("sink"))
        bin.add_pad(sink_pad)
        self.playbin.set_property('audio-sink', rate_bin)
        self.bus = self.pipeline.get_bus()
        self.pipeline.set_state(gst.STATE_NULL)
        music_stream_uri = self.gtts_stream(self.track_info(track))
        logger.debug("stream: %s" % music_stream_uri)
        self.playbin.set_property('uri', music_stream_uri)
        self.pipeline.set_state(gst.STATE_PLAYING)
        i = 0
        while 42:
            #import pdb; pdb.set_trace()
            msg = self.bus.pop()
            if msg:
                logger.debug(msg)
                logger.debug(i)
                if msg.type == gst.MESSAGE_EOS:
                   break
                if msg.type == gst.MESSAGE_ERROR:
                    logger.error(msg)
                    import pdb; pdb.set_trace()
                    break
            i += 1
            if i > 30000000:
                break
        self.pipeline.set_state(gst.STATE_NULL)
        sleep(0.1)
        

    def end_of_stream(self, bus, message):
        logger.debug(message)
        logger.debug("end of stream")
        return True
