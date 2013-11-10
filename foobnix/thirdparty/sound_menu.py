#!/usr/bin/python
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

    def __init__(self, desktop_name):
        """
        Creates a SoundMenuControls object.

        Requires a dbus loop to be created before the gtk mainloop,
        typically by calling DBusGMainLoop(set_as_default=True).

        arguments:
        desktop_name: The name of the desktop file for the application,
        such as, "simple-player" to refer to the file: simple-player.desktop.

        """

        self.desktop_name = desktop_name
        bus_str = """org.mpris.MediaPlayer2.%s""" % desktop_name
        bus_name = dbus.service.BusName(bus_str, bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, "/org/mpris/MediaPlayer2")
        self.__playback_status = "Stopped"

        self.song_changed()

    def song_changed(self, artists = None, album = None, title = None, cover = None):
        """song_changed - sets the info for the current song.

        This method is not typically overriden. It should be called
        by implementations of this class when the player has changed
        songs.

        named arguments:
            artists - a list of strings representing the artists"
            album - a string for the name of the album
            title - a string for the title of the song

        """

        if artists is None:
            artists = ["Artist Unknown"]
        if album is None:
            album = "Album Uknown"
        if title is None:
            title = "Title Uknown"
        data = {"xesam:album": album,
                "xesam:title": title,
                "xesam:artist": artists
                }
        if cover:
            data["mpris:artUrl"] = cover
        self.__meta_data = dbus.Dictionary(data, "sv", variant_level=1)


    @dbus.service.method('org.mpris.MediaPlayer2')
    def Raise(self):
        """Raise

        A dbus signal handler for the Raise signal. Do no override this
        function directly. rather, overrise _sound_menu_raise. This
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


    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
    def Get(self, interface, prop):
        """Get

        A function necessary to implement dbus properties.

        This function is only called by the Sound Menu, and should not
        be overriden or called directly.

        """

        my_prop = self.__getattribute__(prop)
        return my_prop

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ssv')
    def Set(self, interface, prop, value):
        """Set

        A function necessary to implement dbus properties.

        This function is only called by the Sound Menu, and should not
        be overriden or called directly.

        """
        my_prop = self.__getattribute__(prop)
        my_prop = value

    @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
    def GetAll(self, interface):
        """GetAll

        A function necessary to implement dbus properties.

        This function is only called by the Sound Menu, and should not
        be overriden or called directly.

        """

        return [DesktopEntry, PlaybackStatus, MetaData]

    @property
    def DesktopEntry(self):
        """DesktopEntry

        The name of the desktop file.

        This propert is only used by the Sound Menu, and should not
        be overriden or called directly.

        """

        return self.desktop_name

    @property
    def PlaybackStatus(self):
        """PlaybackStatus

        Current status "Playing", "Paused", or "Stopped"

        This property is only used by the Sound Menu, and should not
        be overriden or called directly.

        """

        return self.__playback_status

    @property
    def MetaData(self):
        """MetaData

        The info for the current song.

        This property is only used by the Sound Menu, and should not
        be overriden or called directly.

        """

        return self.__meta_data

    @dbus.service.method('org.mpris.MediaPlayer2.Player')
    def Next(self):
        """Next

        A dbus signal handler for the Next signal. Do no override this
        function directly. Rather, overide _sound_menu_next. This
        function is typically only called by the Sound, not directly
        from code.

        """

        self._sound_menu_next()

    def _sound_menu_next(self):
        """_sound_menu_next

        This function is called when the user has clicked
        the next button in the Sound Indicator. Implementations
        should overrirde this function in order to a function to
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
        function directly. Rather, overide _sound_menu_previous. This
        function is typically only called by the Sound Menu, not directly
        from code.

        """


        self._sound_menu_previous()

    def _sound_menu_previous(self):
        """_sound_menu_previous

        This function is called when the user has clicked
        the previous button in the Sound Indicator. Implementations
        should overrirde this function in order to a function to
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
        function directly. Rather, overide _sound_menu_next. This
        function is typically only called by the Sound, not directly
        from code.

        """

        if not self._sound_menu_is_playing():
            self._sound_menu_play()
            self.signal_playing()
        else:
            self._sound_menu_pause()
            self.signal_paused()

    def signal_playing(self):
        """signal_playing - Tell the Sound Menu that the player has
        started playing. Implementations many need to call this function in order
        to keep the Sound Menu in synch.

        arguments:
            none

        """
        self.__playback_status = "Playing"
        d = dbus.Dictionary({"PlaybackStatus":self.__playback_status, "Metadata":self.__meta_data},
                            "sv",variant_level=1)
        self.PropertiesChanged("org.mpris.MediaPlayer2.Player",d,[])

    def signal_paused(self):
        """signal_paused - Tell the Sound Menu that the player has
        been paused. Implementations many need to call this function in order
        to keep the Sound Menu in synch.

        arguments:
            none

        """

        self.__playback_status = "Paused"
        d = dbus.Dictionary({"PlaybackStatus":self.__playback_status},
                            "sv",variant_level=1)
        self.PropertiesChanged("org.mpris.MediaPlayer2.Player",d,[])

    def signal_stopped(self):
        self.__playback_status = "Stopped"
        d = dbus.Dictionary({"PlaybackStatus": self.__playback_status},
                            "sv", variant_level=1)
        self.PropertiesChanged("org.mpris.MediaPlayer2.Player", d, [])

    def _sound_menu_is_playing(self):
        """_sound_menu_is_playing

        Check if the the player is playing,.
        Implementations should overrirde this function
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

        Reponds to the Sound Menu when the user has click the
        Pause button.

        Implementations should overrirde this function
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

        Reponds to the Sound Menu when the user has click the
        Play button.

        Implementations should overrirde this function
        to play playback when called.

        The default implementation of this function does nothing

        arguments:
            none

        returns:
            None

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