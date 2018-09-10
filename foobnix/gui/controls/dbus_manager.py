#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: anton.komolov
'''

import logging
import dbus.service

from foobnix.fc.fc import FC
from foobnix.util import idle_task
from foobnix.version import FOOBNIX_VERSION
from dbus.mainloop.glib import DBusGMainLoop
from foobnix.gui.service.path_service import get_foobnix_resourse_path_by_name
from foobnix.thirdparty.sound_menu import SoundMenuControls
from foobnix.util.const import STATE_PLAY, ICON_FOOBNIX, FTYPE_RADIO

DBusGMainLoop(set_as_default=True)

DBUS_NAME = "org.mpris.MediaPlayer2.foobnix"
MPRIS_ROOT_PATH = "/"
MPRIS_PLAYER_PATH = "/Player"
MPRIS_TRACKLIST_PATH = "/TrackList"
DBUS_MEDIAPLAYER_INTERFACE = 'org.freedesktop.MediaPlayer'


class DBusManager():
    def __init__(self, controls):
        try:
            self.sound_menu = MprisSoundMenu(controls)
            self.player = MprisPlayer(controls)
        except Exception, e:
            self.sound_menu = None
            logging.error("DBUS Initialization Error " + str(e))

        '''
        try:
            dbus_interface = 'org.gnome.SettingsDaemon.MediaKeys'
            mm_object = bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')

            mm_object.GrabMediaPlayerKeys("MyMultimediaThingy", 0, dbus_interface=dbus_interface)
            mm_object.connect_to_signal('MediaPlayerKeyPressed', self.on_mediakey)
            #mm_object.ReleaseMediaPlayerKeys("MyMultimediaThingy", dbus_interface=dbus_interface)
        except Exception, e:
            self.sound_menu = None
            logging.error("DBUS Initialization Error " + str(e))
        '''

    def _set_state_play(self):
        if self.sound_menu:
            self.sound_menu.signal_playing()

    def _set_state_pause(self):
        if self.sound_menu:
            self.sound_menu.signal_paused()

    def _set_state_stop(self):
        if self.sound_menu:
            self.sound_menu.signal_stopped()

    def _update_info(self, bean):
        if not bean:
            return
        if not self.sound_menu:     # if dbus initialization can't be finished
            return
        image = "file:///" + get_foobnix_resourse_path_by_name(ICON_FOOBNIX)
        if bean.image:
            if bean.image.startswith("/"):
                image = "file:///" + bean.image
            else:
                image = bean.image
        artists = None
        if bean.artist:
            artists = [bean.artist]
        properties = {
            "CanPause": bean.type != FTYPE_RADIO,
            "CanSeek": bean.type != FTYPE_RADIO
            }
        self.sound_menu.song_changed(artists=artists,
                                     title=bean.title or bean.text,
                                     album=bean.album,
                                     cover=image,
                                     duration_microsec=self.sound_menu.duration_microseconds,
                                     properties=properties)

    def on_mediakey(self, comes_from, what):
        if not FC().media_keys_enabled:
            return
        logging.debug("Multi media key pressed" + what)
        """
        gets called when multimedia keys are pressed down.
        """
        if what in ['Stop', 'Play', 'Next', 'Previous']:
            if what == 'Stop':
                self.controls.state_stop()
            elif what == 'Play':
                self.controls.state_play_pause()
            elif what == 'Next':
                self.controls.next()
            elif what == 'Previous':
                self.controls.prev()
        else:
            logging.debug('Got a multimedia key:' + str(what))


class MprisPlayer(dbus.service.Object):
    """implementation org.mpris.MediaPlayer2.foobnix /Player"""


    def __init__(self, controls):
        self.controls = controls

        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(DBUS_NAME, bus=bus)
        dbus.service.Object.__init__(self, bus_name, MPRIS_PLAYER_PATH)

    @dbus.service.signal(DBUS_MEDIAPLAYER_INTERFACE, signature='ss')
    def current(self, track, info):
        return "%s is playing [%s]" % (track, info)

    #Next ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Next(self):
        self.controls.next()

    #Prev ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Previous(self):
        self.controls.prev()

    #Pause ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Pause(self):
        self.controls.state_pause()

    #Stop ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Stop(self):
        self.controls.state_stop()

    #Play ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Play(self):
        self.controls.state_play()

    #PlayPause for test
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def PlayPause(self):
        self.controls.state_play_pause()

    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='s')
    def Identity(self):
        return "foobnix %s" % FOOBNIX_VERSION

    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='(qq)')
    def MprisVersion(self):
        return 1, 0

    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Quit(self):
        self.controls.quit()

    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='s')
    def parse_arguments(self, args):
        if args and len(args) > 0:
            self.controls.check_for_media(args)
            result = self.check_for_commands(args)
            if not result:
                self.controls.show()
            if type(result).__name__ == 'str':
                return result
        return "Other copy of player is run"

    def check_for_commands(self, args):
        if len(args) == 1:
            command = args[0]

        elif len(args) == 2:
            command = args[1]
        else:
            return False

        if "--next" == command:
            self.controls.next()
        elif "--prev" == command:
            self.controls.prev()
        elif "--stop" == command:
            self.controls.state_stop()
        elif "--pause" == command:
            self.controls.state_pause()
        elif "--play" == command:
            self.controls.state_play()
        elif "--volume-up" == command:
            self.controls.volume_up()
        elif "--volume-down" == command:
            self.controls.volume_down()
        elif "--mute" == command:
            self.controls.mute()
        elif "--show-hide" == command:
            self.controls.show_hide()
        elif "--show" == command:
            self.controls.show()
        elif "--hide" == command:
            self.controls.hide()
        elif "--play-pause" == command:
            self.controls.play_pause()
        elif "--download" == command:
            self.controls.download()
        elif "--version" == command:
            return FOOBNIX_VERSION
        elif "--state" == command:
            return self.controls.media_engine.current_state
        elif "--now-playing" == command:
            bean = self.controls.notetabs.get_current_tree().get_current_bean_by_UUID()
            if bean:
                return bean.get_display_name()
        else:
            return False
        return True


class MprisSoundMenu(SoundMenuControls):
    def __init__(self, controls):
        self.controls = controls
        SoundMenuControls.__init__(self, "foobnix %s" % FOOBNIX_VERSION, "foobnix")


    def _sound_menu_next(self):
        self.controls.next()

    def _sound_menu_previous(self):
        self.controls.prev()

    def _sound_menu_is_playing(self):
        return self.controls.media_engine.current_state is STATE_PLAY

    def _sound_menu_play(self):
        self.controls.state_play()

    def _sound_menu_pause(self):
        self.controls.state_pause()
    
    def _sound_menu_stop(self):
        self.controls.state_stop()

    @idle_task
    def _sound_menu_raise(self):
        self.controls.main_window.show()
    
    @idle_task
    def _sound_menu_quit(self):
        self.controls.quit()

    def _sound_menu_seek(self, offset):
        self.controls.player_seek_microseconds_relative(offset)

    def _sound_menu_set_position(self, position):
        self.controls.player_seek_microseconds(position)

    def _sound_menu_get_volume(self):
        return self.controls.get_player_volume() / 100.0

    def _sound_menu_set_volume(self, value):
        if value > 1.0:
            value = 1.0
        elif value < 0.0:
            value = 0.0

        return self.controls.player_volume(100.0*value)

    @property
    def position_microseconds(self):
        return self.controls.position_microseconds

    @property
    def duration_microseconds(self):
        return self.controls.duration_microseconds


def foobnix_dbus_interface():
    try:
        bus = dbus.SessionBus()
        dbus_objects = dbus.Interface(bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus'),
                                      'org.freedesktop.DBus').ListNames()

        if not DBUS_NAME in dbus_objects:
            return None
        else:
            return dbus.Interface(bus.get_object(DBUS_NAME, MPRIS_PLAYER_PATH), DBUS_MEDIAPLAYER_INTERFACE)
    except Exception, e:
        logging.error("Dbus error", e)
        return None
