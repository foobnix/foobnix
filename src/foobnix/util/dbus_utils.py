#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: anton.komolov
'''
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from foobnix.util.configuration import get_version
import os
import thread

DBusGMainLoop(set_as_default=True)

DBUS_NAME = "org.mpris.foobnix"
DBUS_OBJECT_PATH = "/FoobnixObject"
MPRIS_ROOT_PATH = "/"
MPRIS_PLAYER_PATH = "/Player"
MPRIS_TRACKLIST_PATH = "/TrackList"
DBUS_MAIN_INTERFACE = 'org.mpris.foobnix'
DBUS_MEDIAPLAYER_INTERFACE = 'org.freedesktop.MediaPlayer'

class MprisRoot(dbus.service.Object):
    def __init__(self, interface, object_path=MPRIS_ROOT_PATH):
        self.interface = interface
        dbus.service.Object.__init__(self, dbus.SessionBus(), object_path)

    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='s')
    def Identity(self):
        return "foobnix %s" % get_version()

    @dbus.service.method (DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='(qq)')
    def MprisVersion (self):
        return (1, 0)

    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Quit(self):
        self.interface.app.exit()

class MprisPlayer(dbus.service.Object):
    def __init__(self, interface, object_path=MPRIS_PLAYER_PATH):
        self.interface = interface
        dbus.service.Object.__init__(self, dbus.SessionBus(), object_path)

    #Next ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Next(self):
        self.interface.app.action_command(['--next'])

    #Prev ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Prev(self):
        self.interface.app.action_command(['--prev'])

    #Pause ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Pause(self):
        self.interface.app.action_command(['--pause'])

    #Stop ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Stop(self):
        self.interface.app.action_command(['--stop'])

    #Play ( )
    @dbus.service.method(DBUS_MEDIAPLAYER_INTERFACE, in_signature='', out_signature='')
    def Play(self):
        self.interface.app.action_command(['--play'])

    #TODO
    #Repeat ( b: State )
    """State − b
       TRUE to repeat the current track, FALSE to stop repeating."""
    #GetStatus ( ) → (iiii)
    """Return the status of media player as a struct of 4 ints.
       Returns
       Status − (iiii) (Status_Struct)
       Status_Struct − ( i: Playback_State, i: Shuffle_State, i: Repeat_Current_State, i: Endless_State )
       Playback_State − i
        0 = Playing, 1 = Paused, 2 = Stopped.
       Shuffle_State − i
        0 = Playing linearly, 1 = Playing randomly.
       Repeat_Current_State − i
        0 = Go to the next element once the current has finished playing, 1 = Repeat the current element.
       Endless_State − i
        0 = Stop playing once the last element has been played, 1 = Never give up playing"""
    #GetMetadata ( ) → a{sv}
    """Gives all meta data available for the currently played element.
       Guidelines for field names are at http://wiki.xmms2.xmms.se/wiki/MPRIS_Metadata .
       Returns Metadata − a{sv} (String_Variant_Map)"""
    #GetCaps ( ) → i
    """Return the "media player"'s current capabilities.
       Returns Capabilities − i (Caps_Flags)"""
    #VolumeSet ( i: Volume )
    #VolumeGet ( ) → i
    #PositionSet ( i: Position )
    """Track position between [0;<track_length>] in ms."""
    #PositionGet ( ) → i
    """Track position between [0;<track_length>] in ms."""

    #Signals:
    #TrackChange ( a{sv}: Metadata )
    #StatusChange ( (iiii): Status )
    #CapsChange ( i: Capabilities )


class DBusManager(dbus.service.Object):
    def __init__(self, interface, object_path=DBUS_OBJECT_PATH):
        self.interface = interface
        self.bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(DBUS_NAME, bus=self.bus)
        dbus.service.Object.__init__(self, bus_name, object_path)

        MprisRoot(interface)
        MprisPlayer(interface)

        try:
            dbus_interface = 'org.gnome.SettingsDaemon.MediaKeys'
            mm_object = bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')
            mm_object.GrabMediaPlayerKeys("MyMultimediaThingy", 0, dbus_interface=dbus_interface)
            mm_object.connect_to_signal('MediaPlayerKeyPressed', self.on_mediakey)
        except Exception, e:
            print "your OS is not GNOME", e


    @dbus.service.method(DBUS_MAIN_INTERFACE, in_signature='', out_signature='')
    def interactive_play_args(self, args):
        print "manager recive", args
        self.interface.play_args(args)

    def on_mediakey(self, comes_from, what):
        """
        gets called when multimedia keys are pressed down.
        """
        if what in ['Stop', 'Play', 'Next', 'Previous']:
            if what == 'Stop':
                thread.start_new_thread(os.system, ("foobnix --stop",))
            elif what == 'Play':
                thread.start_new_thread(os.system, ("foobnix --play-pause",))
            elif what == 'Next':
                thread.start_new_thread(os.system, ("foobnix --next",))
            elif what == 'Previous':
                thread.start_new_thread(os.system, ("foobnix --prev",))
        else:
            print ('Got a multimedia key...')

def getFoobnixDBusInterface():
    bus = dbus.SessionBus()
    dbus_objects = dbus.Interface(bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus'), 'org.freedesktop.DBus').ListNames()
    if not DBUS_NAME in dbus_objects:
        return None
    else:
        return dbus.Interface(bus.get_object(DBUS_NAME, DBUS_OBJECT_PATH), DBUS_MAIN_INTERFACE)

