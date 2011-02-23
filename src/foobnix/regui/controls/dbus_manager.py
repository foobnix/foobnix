#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: anton.komolov
'''
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from foobnix.regui.model.signal import FControl
from foobnix.version import FOOBNIX_VERSION
import logging

DBusGMainLoop(set_as_default=True)

DBUS_NAME = "org.mpris.foobnix"
MPRIS_ROOT_PATH = "/"
MPRIS_PLAYER_PATH = "/Player"
MPRIS_TRACKLIST_PATH = "/TrackList"
DBUS_MEDIAPLAYER_INTERFACE = 'org.freedesktop.MediaPlayer'

class MprisPlayer(dbus.service.Object, FControl):
    def __init__(self, controls, object_path=MPRIS_PLAYER_PATH):
        dbus.service.Object.__init__(self, dbus.SessionBus(), object_path)
        FControl.__init__(self, controls)

    #Next ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Next(self):
        self.controls.next()

    #Prev ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Prev(self):
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

class DBusManager(dbus.service.Object, FControl):
    def __init__(self, controls, object_path=MPRIS_ROOT_PATH):
        FControl.__init__(self, controls)
        try:
            bus = dbus.SessionBus()
            bus_name = dbus.service.BusName(DBUS_NAME, bus=bus)
            dbus.service.Object.__init__(self, bus_name, object_path)
    
            self._player = MprisPlayer(controls)
        
            dbus_interface = 'org.gnome.SettingsDaemon.MediaKeys'
            mm_object = bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')
            mm_object.GrabMediaPlayerKeys("MyMultimediaThingy", 0, dbus_interface=dbus_interface)
            mm_object.connect_to_signal('MediaPlayerKeyPressed', self.on_mediakey)
        except Exception, e:
            logging.error("DBUS Initialization Error" + str(e))
    
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
            self.controls.playState()
        elif "--volume-up" == command:
            self.controls.volume_up()
        elif "--volume-down" == command:
            self.controls.volume_down()
        elif "--show-hide" == command:
            self.controls.show_hide()
        elif "--show" == command:
            self.controls.show()
        elif "--hide" == command:
            self.controls.hide()
        elif "--play-pause" == command:
            self.controls.play_pause()
        elif "--version" == command:
            return FOOBNIX_VERSION
        elif "--state" == command:
            return self.controls.media_engine.current_state
        elif "--now-playing" == command:
            bean = self.controls.notetabs.get_active_tree().get_current_bean_by_UUID()
            if bean:
                return bean.get_display_name()
        else:
            return False
        return True
    
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
        
                
    def on_mediakey(self, comes_from, what):
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

    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='s')
    def Identity(self):
        return "foobnix %s" % FOOBNIX_VERSION

    @dbus.service.method (DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='(qq)')
    def MprisVersion (self):
        return (1, 0)

    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Quit(self):
        self.controls.quit()

def foobnix_dbus_interface():
    try:
        bus = dbus.SessionBus()
        dbus_objects = dbus.Interface(bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus'), 'org.freedesktop.DBus').ListNames()
        if not DBUS_NAME in dbus_objects:
            return None
        else:
            return dbus.Interface(bus.get_object(DBUS_NAME, MPRIS_ROOT_PATH), DBUS_MEDIAPLAYER_INTERFACE)
    except Exception, e:
        logging.error("Dbus error", e)
        return None
