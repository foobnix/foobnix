# -*- coding: utf-8 -*-
### BEGIN LICENSE
# Copyright (C) 2011 Rick Spencer <rick.spencer@canonical.com>
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

"""Contains SoundMenuControls, A class to make it easy to integrate with the Ubuntu Sound Menu.

In order for a media player to appear in the sonud menu, it must have
a desktop file in /usr/share/applications. For example, for a media player
named "simple" player, there must be desktop file /usr/share/applications/simple-player.desktop

The desktop file must specify that it is indeed a media player. For example, simple-player.desktop
might look like the follwing:
[Desktop Entry]
Name=Simple Player
Comment=SimplePlayer application
Categories=GNOME;Audio;Music;Player;AudioVideo;
Exec=simple-player
Icon=simple-player
Terminal=false
Type=Application
MimeType=application/x-ogg;application/ogg;audio/x-vorbis+ogg;audio/x-scpls;audio/x-mp3;audio/x-mpeg;audio/mpeg;audio/x-mpegurl;audio/x-flac;

In order for the sound menu to run, a dbus loop must be running before
the player is created and before the Gtk. mainloop is run. you can add
DBusGMainLoop(set_as_default=True) to your application's __main__ function.

The Ubuntu Sound Menu integrates with applications via the MPRIS2 dbus api,
which is specified here: http://www.mpris.org/2.1/spec/

This module does strive to provide an MPRIS2 implementation, but rather
focuses on the subset of functionality required by the Sound Menu.

The SoundMenuControls class can be ininstatiated, but does not provide any
default functionality. In order to provide the required functionality,
implementations must be provided for the functions starting with
"_sound_menu", such as "_sound_menu_play", etc...

Functions and properties starting with capitalize letters, such as
"Next" and "Previous" are called by the Ubuntu Sound Menu. These
functions and properties are not designed to be called directly
or overriden by application code, only the Sound Menu.

Other functions are designed to be called as needed by the
implementation to inform the Sound Menu of changes. Thse functions
include signal_playing, signal_paused, and song_changed.

Using
#create the sound menu object and reassign functions
sound_menu = SoundMenuControls(desktop_name)
sound_menu._sound_menu_next = _sound_menu_next
sound_menu._sound_menu_previous = _sound_menu_previous
sound_menu._sound_menu_is_playing = _sound_menu_is_playing
sound_menu._sound_menu_play = _sound_menu_play
sound_menu._sound_menu_pause = _sound_menu_play
sound_menu._sound_menu_raise = _sound_menu_raise

#when the song in the player changes, it should inform
the sond menu
sound_menu.song_changed(artist,album,title)

#when the player changes to/from the playing, it should inform the sound menu
sound_menu.signal_playing()
sound_menu.signal_paused()

#whent the song is changed from the application,
#use song_changed to inform the Ubuntu Sound Menu
sound_menu.song_changed(artist, album, song_title)

Configuring
SoundMenuControls does not come with any stock behaviors, so it
cannot be configured

Extending
SoundMenuControls can be used as a base class with single or multiple inheritance.

_sound_menu_next
_sound_menu_previous
_sound_menu_is_playing
_sound_menu_play
_sound_menu_pause

"""

import dbus
import dbus.service

class SoundMenuControls(dbus.service.Object):
    """
    SoundMenuControls - A class to make it easy to integrate with the Ubuntu Sound Menu.

    """

    def __init__(self, identity, desktop_name):
        """
        Creates a SoundMenuControls object.

        Requires a dbus loop to be created before the gtk mainloop,
        typically by calling DBusGMainLoop(set_as_default=True).

        arguments:
        desktop_name: The name of the desktop file for the application,
        such as, "simple-player" to refer to the file: simple-player.desktop.

        """

        bus_str = """org.mpris.MediaPlayer2.%s""" % desktop_name
        bus_name = dbus.service.BusName(bus_str, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/org/mpris/MediaPlayer2")
        
        self._static_properties = {
            "PlaybackStatus": "Stopped",
            "CanQuit": True,
            "CanRaise": True,
            "HasTrackList": False,
            "Identity": identity,
            "DesktopEntry": desktop_name,
            "Rate": 1.0,
            "MinimumRate": 1.0,
            "MaximumRate": 1.0,
            "CanGoNext": True,
            "CanGoPrevious": True,
            "CanPlay": True,
            "CanPause": True,
            "CanSeek": True,
            "CanControl": True,
            }
        
        self._volatile_properties = {
            "Position": lambda: dbus.Int64(self.position_microseconds),
            "Volume": self._sound_menu_get_volume
            }

        self._properties_setters = {
            "Volume": self._sound_menu_set_volume
            }

        self.song_changed()
    
    def get_property(self, name):
        if name in self._static_properties:
            return self._static_properties[name]
        elif name in self._volatile_properties:
            return self._volatile_properties[name]()
        
        return None
    
    def get_all_properties(self):
        properties = {key: prop_getter() for key, prop_getter in self._volatile_properties.items()}
        properties.update(self._static_properties)
        return properties
    
    def set_property(self, name, value):
        self._static_properties[name] = value

    def set_properties(self, **kwargs):
        self._static_properties.update(kwargs)

    def song_changed(self, artists = None, album = None, title = None, cover = None, duration_microsec = 0, properties = {}):
        """song_changed - sets the info for the current song.

        This method is not typically overriden. It should be called
        by implementations of this class when the player has changed
        songs.

        named arguments:
            artists - a list of strings representing the artists"
            album - a string for the name of the album
            title - a string for the title of the song
            cover - a string for the location (URI) of the track image
            duration_microsec - track duration in microseconds
            properties - a dictionary of MediaPlayer2.Player properties
                         that are specific to this track
                         (e.g. {"CanSeek": False})

        """

        if artists is None:
            artists = ["Artist Unknown"]
        if album is None:
            album = "Album Uknown"
        if title is None:
            title = "Title Uknown"

        data = {
            "mpris:trackid": "/Player/TrackList/" + self._get_track_id(title),
            "mpris:length": duration_microsec,
            "xesam:album": album,
            "xesam:title": title,
            "xesam:artist": artists
            }

        if cover:
            data["mpris:artUrl"] = cover

        self.set_property("Metadata", dbus.Dictionary(data, "sv", variant_level=1))
        self.set_properties(**properties)
        self.properties_changed("Metadata", *properties.keys())

    @staticmethod
    def _get_track_id(title):
        return "".join(filter(str.isalnum, str(title)))

    @dbus.service.method('org.mpris.MediaPlayer2')
    def Raise(self):
        """Raise

        A dbus signal handler for the Raise signal. Do no override this
        function directly. rather, override _sound_menu_raise. This
        function is typically only called by the Sound, not directly
        from code.

        """

        self._sound_menu_raise()

    def _sound_menu_raise(self):
        """ _sound_menu_raise -

        Override this function to bring the media player to the front
        when selected by the sound menu. For example, by calling
        app_window.get_window().show()

        """

        raise NotImplementedError("""@dbus.service.method('org.mpris.MediaPlayer2') Raise
                                      is not implemented by this player.""")
    
    
    @dbus.service.method('org.mpris.MediaPlayer2')
    def Quit(self):
        """Quit

        A dbus signal handler for the Quit signal. Do no override this
        function directly. rather, override _sound_menu_quit. This
        function is typically only called by the Sound, not directly
        from code.

        """

        self._sound_menu_quit()

    def _sound_menu_quit(self):
        """ _sound_menu_quit -

        Override this function to quit the application when selected
        by the sound menu.

        """

        raise NotImplementedError("""@dbus.service.method('org.mpris.MediaPlayer2') Quit
                                      is not implemented by this player.""")


    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        """Get

        A function necessary to implement dbus properties.

        This function is only called by the Sound Menu, and should not
        be overriden or called directly.

        """

        return self.get_property(prop)

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ssv')
    def Set(self, interface, prop, value):
        """Set

        A function necessary to implement dbus properties.

        This function is only called by the Sound Menu, and should not
        be overriden or called directly.

        """
        if prop in self._properties_setters:
            self._properties_setters[prop](value)

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        """GetAll

        A function necessary to implement dbus properties.

        This function is only called by the Sound Menu, and should not
        be overriden or called directly.

        """

        return dbus.Dictionary(self.get_all_properties(), "sv", variant_level=1)

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Next(self):
        """Next

        A dbus signal handler for the Next signal. Do no override this
        function directly. Rather, override _sound_menu_next. This
        function is typically only called by the Sound, not directly
        from code.

        """

        self._sound_menu_next()

    def _sound_menu_next(self):
        """_sound_menu_next

        This function is called when the user has clicked
        the next button in the Sound Indicator. Implementations
        should override this function in order to a function to
        advance to the next track. Implementations should call
        song_changed() and sound_menu.signal_playing() in order to
        keep the song information in the sound menu in sync.

        The default implementation of this function has no effect.

        """
        pass

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Previous(self):
        """Previous

        A dbus signal handler for the Previous signal. Do no override this
        function directly. Rather, override _sound_menu_previous. This
        function is typically only called by the Sound Menu, not directly
        from code.

        """


        self._sound_menu_previous()

    def _sound_menu_previous(self):
        """_sound_menu_previous

        This function is called when the user has clicked
        the previous button in the Sound Indicator. Implementations
        should override this function in order to a function to
        advance to the next track. Implementations should call
        song_changed() and  sound_menu.signal_playing() in order to
        keep the song information in sync.

        The default implementation of this function has no effect.


        """
        pass

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def PlayPause(self):
        """Next

        A dbus signal handler for the Next signal. Do no override this
        function directly. Rather, override _sound_menu_next. This
        function is typically only called by the Sound, not directly
        from code.

        """

        if not self._sound_menu_is_playing():
            self._sound_menu_play()
            self.signal_playing()
        else:
            self._sound_menu_pause()
            self.signal_paused()
    
    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Play(self):
        self._sound_menu_play()
        self.signal_playing()

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Pause(self):
        self._sound_menu_pause()
        self.signal_paused()
        
    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Stop(self):
        self._sound_menu_stop()
        self.signal_stopped()

    def signal_playing(self):
        """signal_playing - Tell the Sound Menu that the player has
        started playing. Implementations many need to call this function in order
        to keep the Sound Menu in synch.

        arguments:
            none

        """

        self.set_property("PlaybackStatus", "Playing")
        self.properties_changed("PlaybackStatus")

    def signal_paused(self):
        """signal_paused - Tell the Sound Menu that the player has
        been paused. Implementations many need to call this function in order
        to keep the Sound Menu in synch.

        arguments:
            none

        """

        self.set_property("PlaybackStatus", "Paused")
        self.properties_changed("PlaybackStatus")

    def signal_stopped(self):
        self.set_property("PlaybackStatus", "Stopped")
        self.properties_changed("PlaybackStatus")

    def _sound_menu_is_playing(self):
        """_sound_menu_is_playing

        Check if the the player is playing,.
        Implementations should override this function
        so that the Sound Menu can check whether to display
        Play or Pause functionality.

        The default implementation of this function always
        returns False.

        arguments:
            none

        returns:
            returns True if the player is playing, otherwise
            returns False if the player is stopped or paused.
        """

        return False

    def _sound_menu_pause(self):
        """_sound_menu_pause

        Responds to the Sound Menu when the user has clicked the
        Pause button.

        Implementations should override this function
        to pause playback when called.

        The default implementation of this function does nothing

        arguments:
            none

        returns:
            None

        """

        pass

    def _sound_menu_play(self):
        """_sound_menu_play

        Responds to the Sound Menu when the user has clicked the
        Play button.

        Implementations should override this function
        to play playback when called.

        The default implementation of this function does nothing

        arguments:
            none

        returns:
            None

        """

        pass
    
    def _sound_menu_stop(self):
        """_sound_menu_play

        Responds to the Sound Menu when the user has clicked the
        Stop button.

        Implementations should override this function
        to stop playback when called.

        The default implementation of this function does nothing

        arguments:
            none

        returns:
            None

        """
        
        pass

    @dbus.service.method('org.mpris.MediaPlayer2.Player', signature='x')
    def Seek(self, offset):
        self._sound_menu_seek(offset)

    def _sound_menu_seek(self, offset):
        pass

    @dbus.service.method('org.mpris.MediaPlayer2.Player', signature='ox')
    def SetPosition(self, track_id, position):
        self._sound_menu_set_position(position)

    def _sound_menu_set_position(self, position):
        pass

    def _sound_menu_get_volume(self):
        """Implementations should override this function
        to return the correct value
        """
        return 1.0

    def _sound_menu_set_volume(value):
        """Implementations should override this function
        to set the volume level to _value_
        """
        pass

    @dbus.service.signal(dbus.PROPERTIES_IFACE, signature='sa{sv}as')
    def PropertiesChanged(self, interface_name, changed_properties,
                          invalidated_properties):
        """PropertiesChanged

        A function necessary to implement dbus properties.

        Typically, this function is not overriden or called directly.

        """

        pass
    
    def properties_changed(self, *args):
        props = {prop: self.get_property(prop) for prop in args}
        d = dbus.Dictionary(props, "sv", variant_level=1)
        self.PropertiesChanged("org.mpris.MediaPlayer2.Player", d, [])
