#!/usr/bin/python

__metaclass__ = type

import md5
import os
import socket
import sys
import time
from pprint import pformat
from urllib2 import urlopen, HTTPError

import pygtk
pygtk.require('2.0')

import pygst
pygst.require('0.10')

import gtk
import gtk.glade
import gst

from twisted.internet import gtk2reactor
gtk2reactor.install()

from twisted.protocols import basic
from twisted.internet import protocol, reactor, error

decoder = 'mad'
sink = 'gconfaudiosink'
config_file = os.path.expanduser('~/.olaf/config')
socket = os.path.expanduser('~/.olaf/socket')

def debug(s):
    if 'OLAF_DEBUG' in os.environ:
        print s

def parse_dict(s):
    return dict([line.split('=', 1) for line in s.splitlines()])

def _test_parse_dict():
    r"""
    >>> parse_dict('')
    {}
    >>> parse_dict('foo=1\nbar=2')
    {'foo': '1', 'bar': '2'}
    """

def strip_dict(D):
    stripped = {}

    for key, value in D.iteritems():
        stripped[key.strip()] = value.strip()

    return stripped

def _test_strip_dict():
    r"""
    >>> strip_dict({})
    {}
    >>> strip_dict({'foo': 'bar'})
    {'foo': 'bar'}
    >>> strip_dict({' foo ': ' bar '})
    {'foo': 'bar'}
    """

class Config:
    def from_file(klass, path):
        if not os.path.exists(path):
            raise RuntimeError("configuration file %s not found" % path)

        data = file(path).read()
        return strip_dict(parse_dict(data))

    from_file = classmethod(from_file)

    def __init__(self, config_dict):
        for required in ('username', 'password'):
            if required not in config_dict:
                raise RuntimeError(
                    "required parameter '%s' not found in configuration" %
                    required)

        self.__getitem__ = config_dict.__getitem__

def _test_config():
    """
    >>> Config({})
    Traceback (most recent call last):
    ...
    RuntimeError: required parameter 'username' not found in configuration
    >>> config = Config({'username': 'bob', 'password': 'secret'})
    >>> config['username']
    'bob'
    """

class Track:
    def __init__(self, track_info):
        self.artist = track_info.get('artist')
        self.album = track_info.get('album')
        self.title = track_info.get('track')
        self.url = track_info.get('track_url')
        self.length = int(track_info['trackduration'])
        minutes, seconds = divmod(self.length, 60)
        self.length_string = '%d:%02d' % (minutes, seconds)
        image = track_info.get('albumcover_medium')

        if image and not image.endswith('/'):
            self.image = image
        else:
            self.image = None

    def summary(self):
        info = [s for s in [self.artist, self.album, self.title] if s]

        if info:
            return ' / '.join(info)
        else:
            return '(no info)'

    def _format(self):
        _track = {}
        _track['album'] = self.album
        _track['artist'] = self.artist
        _track['title'] = self.title
        _track['length'] = self.length
        return pformat(_track)

class LastfmRadio:
    def __init__(self, username, password_md5):
        self.session_info = self._get_session(username, password_md5)
        self.session = self.session_info['session']
        assert self.session != 'FAILED'
        self.track = None
        self.stream = None

    def get_stream(self):
        if not self.stream:
            self.stream = self._make_stream(self.session_info['stream_url'])

        return self.stream

    def _make_stream(self, url):
        return urlopen(url)

    def _get_url(self, url):
        url = 'http://ws.audioscrobbler.com/radio/' + url
        return urlopen(url).read()

    def _get_dict_url(self, url):
        return parse_dict(self._get_url(url))

    def _get_session(self, username, password_md5):
        return self._get_dict_url('handshake.php?username=%s&passwordmd5=%s' %
            (username, password_md5))

    def _get_np(self):
        return self._get_dict_url('np.php?session=' + self.session)

    def get_track(self):
        try:
            track = self._get_np()
        except HTTPError:
            return None

        self.track = Track(track)
        debug(self.track._format())
        return self.track

    def skip(self):
        self._get_url('control.php?command=skip&session=' + self.session)

    def ban(self):
        self._get_url('control.php?command=ban&session=' + self.session)

    def love(self):
        self._get_url('control.php?command=love&session=' + self.session)

    def tune(self, url):
        debug(self._get_url('adjust.php?session=%s&url=%s' % (self.session, url)))

    def set_discovery(self, setting):
        if setting:
            url = 'lastfm://settings/discovery/on'
        else:
            url = 'lastfm://settings/discovery/off'

        self._get_url('adjust.php?session=%s&url=%s' % (self.session, url))

class Pipeline:
    def __init__(self, input, decoder, sink, track_callback):
        pipeline = ' ! '.join([
            'fdsrc name=fdsrc fd=%d' % input.fileno(),
            decoder,
            'audioconvert',
            'volume name=volume',
            sink])
        self.bin = gst.parse_launch(pipeline)
        fdsrc = self.bin.get_by_name('fdsrc')
        pad = fdsrc.get_pad('src')
        pad.add_buffer_probe(self._buffer_probe_cb)
        self.track_callback = track_callback
        self._fade_call = None

    def _buffer_probe_cb(self, pad, buffer):
        if 'SYNC' in str(buffer):
            reactor.callInThread(self.track_callback)

        return True

    def play(self):
        self.bin.set_state(gst.STATE_PLAYING)

    def pause(self):
        self.bin.set_state(gst.STATE_PAUSED)

    def get_volume(self):
        elem = self.bin.get_by_name('volume')
        return elem.get_property('volume')

    def _set_volume(self, volume):
        #print '_set_volume: %f' % volume
        elem = self.bin.get_by_name('volume')
        elem.set_property('volume', volume)

    def set_volume(self, volume):
        if self._fade_call and self._fade_call.active():
            self._fade_call.cancel()

        self._set_volume(volume)

    def fade(self):
        volume = self.get_volume()

        if volume < 0.01:
            self.set_volume(0)
            self._fade_call = None
        else:
            self._set_volume(0.8 * volume)
            self._fade_call = reactor.callLater(0.1, self.fade)

def find_data_file (name):
    paths = ('.', '/usr/share/olaf', '/usr/local/share/olaf',
        os.path.dirname(sys.argv[0]))

    for path in paths:
        joined = os.path.join(path, name)

        if os.path.exists(joined):
            return joined

    raise RuntimeError("failed to find data file '%s'" % name)

class Player:
    def __init__(self, config, url=None):
        self.config = config
        self.url = url
        self.track_summary = None
        self.new_track_callback = None
        self.pipeline = None

        glade = gtk.glade.XML(find_data_file('olaf.glade'))
        glade.signal_autoconnect(self)
        self.window = glade.get_widget('window')
        self.image = glade.get_widget('image')
        self.play_button = glade.get_widget('play_button')
        self.skip_button = glade.get_widget('skip_button')
        self.ban_button = glade.get_widget('ban_button')
        self.love_button = glade.get_widget('love_button')
        self.artist_label = glade.get_widget('artist_label')
        self.album_label = glade.get_widget('album_label')
        self.track_label = glade.get_widget('track_label')
        self.length_label = glade.get_widget('length_label')

        reactor.callWhenRunning(self.play_button.clicked)

    def _play(self):
        self.play_button.set_label('gtk-media-stop')
        password_md5 = md5.md5(self.config['password']).hexdigest()
        self.radio = LastfmRadio(self.config['username'], password_md5)

        if self.url:
            self.radio.tune(self.url)

        self.radio.set_discovery(True)
        stream = self.radio.get_stream()
        # jitter hack
        time.sleep(1)
        self.pipeline = Pipeline(stream, decoder, sink, self._cb_new_track)
        self.pipeline.play()

    def _stop(self):
        if self.pipeline:
            self.play_button.set_label('gtk-media-play')
            self.pipeline.pause()
            self.pipeline = None

    def _cb_play(self, button):
        if self.pipeline:
            self._stop()
        else:
            self._play()

    def _cb_skip(self, button):
        self.skip_button.set_sensitive(False)
        reactor.callInThread(self._skip)

    def _cb_ban(self, button):
        self.ban_button.set_sensitive(False)
        reactor.callInThread(self.radio.ban)

    def _cb_love(self, button):
        self.love_button.set_sensitive(False)
        reactor.callInThread(self.radio.love)

    def _schedule_track_update(self, delay):
        self.new_track_callback = reactor.callLater(delay, self._cb_new_track)

    def _skip(self):
        if self.new_track_callback and self.new_track_callback.active():
            self.new_track_callback.cancel()

        self.pipeline.fade()
        self.radio.skip()

    def _quit(self, window):
        self._stop()
        reactor.stop()

    def _cb_new_track(self):
        self.pipeline.set_volume(1)
        self.skip_button.set_sensitive(True)
        self.ban_button.set_sensitive(True)
        self.love_button.set_sensitive(True)
        reactor.callInThread(self._update_track)

    def _update_track(self):
        track = self.track = self.radio.get_track()

        if track is None:
            self._schedule_track_update(5)
            return

        new_summary = track.summary()

        if new_summary == self.track_summary:
            self._schedule_track_update(5)
            return

        self._set_track(track)
        self.track_summary = new_summary

    def _set_track(self, track):
        self.artist_label.set_text(track.artist or '')
        self.album_label.set_text(track.album or '')
        self.track_label.set_text(track.title or '')
        self.length_label.set_text(track.length_string)
        self.image.set_from_file(find_data_file('unknown.png'))
        reactor.callInThread(self._update_image)
        self.window.resize(1, 1)

    def _update_image(self):
        image = self.track.image

        if image:
            loader = gtk.gdk.PixbufLoader()
            loader.write(urlopen(image).read())
            loader.close()
            pixbuf = loader.get_pixbuf().scale_simple(130, 130,
                gtk.gdk.INTERP_BILINEAR)
            self.image.set_from_pixbuf(pixbuf)

class ControlClient(basic.LineReceiver):
    delimiter = '\n'

    def connectionMade(self):
        if len(self.factory.argv) > 1:
            print >>self.transport, 'tune %s' % self.factory.argv[1]

        print >>self.transport, 'present'
        reactor.stop()

class ControlServer(basic.LineReceiver):
    delimiter = '\n'

    def lineReceived(self, line):
        player = self.factory.player

        if line == 'present':
            player.window.present()
            return

        bits = line.split()

        if bits[0] == 'tune' and len(bits) == 2:
            player.radio.tune(bits[1])
            # seems to only be necessary some of the time
            player.radio.skip()
            player.pipeline.fade()
            return

class ControllerFactory(protocol.ClientFactory):
    protocol = ControlClient

    def __init__(self, config, argv):
        self.config = config
        self.argv = argv

        reactor.connectUNIX(socket, self)

    def clientConnectionFailed(self, connector, reason):
        if os.path.exists(socket):
            os.unlink(socket)

        self.protocol = ControlServer

        try:
            reactor.listenUNIX(socket, self)
        except error.CannotListenError:
            print >>sys.stderr, "failed to listen on control socket"
            reactor.stop()

        if len(self.argv) == 2:
            self.player = Player(self.config, self.argv[1])
        else:
            self.player = Player(self.config)

def run(argv):
    config = Config.from_file(config_file)
    ControllerFactory(config, argv)
    reactor.run()

if __name__ == '__main__':
    run(sys.argv)

