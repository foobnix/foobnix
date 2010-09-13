'''
Created on Mar 14, 2010

@author: ivan
'''
import gtk

from foobnix.window.window_controller import WindowController
from foobnix.player.player_controller import PlayerController
from foobnix.player.player_widgets_cntr import PlayerWidgetsCntl
from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.trayicon import TrayIcon
from foobnix.application.app_configuration_controller import AppConfigurationCntrl
from foobnix.online.online_controller import OnlineListCntr
from foobnix.directory.virtuallist_controller import VirturalLIstCntr
from foobnix.base import BaseController

from foobnix.util.configuration import FConfiguration, VERSION
from foobnix.online.search_panel import SearchPanel
from foobnix.preferences.preferences_window import PreferencesWindow
import sys
from foobnix.online.integration.lastfm import LastFmConnector
from socket import gethostname
import urllib2
from foobnix.helpers.dialog_entry import info_dialog_with_link
from foobnix.util import LOG
import thread
import time

class AppController(BaseController):

    def __init__(self, v):
        BaseController.__init__(self)

        last_fm_connector = LastFmConnector()

        self.player_controller = PlayerController(last_fm_connector)

        #self.playlistCntr = PlaylistCntr(v.playlist, self.player_controller)
        self.onlineCntr = OnlineListCntr(v.gxMain, self.player_controller, last_fm_connector)

        self.playlistCntr = self.onlineCntr

        self.virtualListCntr = VirturalLIstCntr()

        #self.radioListCntr = RadioListCntr(v.gxMain, self.player_controller)

        self.playerWidgets = PlayerWidgetsCntl(v.gxMain, self.player_controller)
        self.player_controller.registerWidgets(self.playerWidgets)
        self.player_controller.registerPlaylistCntr(self.playlistCntr)


        self.directoryCntr = DirectoryCntr(v.gxMain, self.playlistCntr, self.virtualListCntr)
        #self.playlistCntr.registerDirectoryCntr(self.directoryCntr)
        self.appConfCntr = AppConfigurationCntrl(v.gxMain, self.directoryCntr)
        self.onlineCntr.register_directory_cntr(self.directoryCntr)

        self.player_controller.registerOnlineCntr(self.onlineCntr)



        self.main_window_controller = WindowController(v.gxMain, v.gxAbout)


        """show pref window"""


        menu_preferences = v.gxMain.get_widget("menu_preferences")
        menu_preferences.connect("activate", lambda * a:self.pref.show())

        self.tray_icon = TrayIcon(v.gxTrayIcon)
        self.main_window_controller.tray_icon = self.tray_icon
        self.tray_icon.connect('toggle_window_visibility', self.main_window_controller.toggle_visibility)
        self.tray_icon.connect('exit', self.exit)
        self.tray_icon.connect('play', self.player_controller.play)
        self.tray_icon.connect('pause', self.player_controller.pause)
        self.tray_icon.connect('prev', self.player_controller.prev)
        self.tray_icon.connect('next', self.player_controller.next)
        self.tray_icon.connect('volume_up', self.player_controller.volume_up)
        self.tray_icon.connect('volume_down', self.player_controller.volume_down)

        self.player_controller.connect('song_playback_started', self.tray_icon.on_song_started)
        self.player_controller.connect('song_playback_started', self.main_window_controller.on_song_started)

        self.main_window_controller.connect('exit', self.exit)

        self.search_panel = SearchPanel(v.gxMain, last_fm_connector)
        self.search_panel.connect('show_search_results', self.onlineCntr.show_results)
        self.search_panel.connect('show_searching_line', self.onlineCntr.show_searching)

        self.pref = PreferencesWindow(self.directoryCntr, self.onlineCntr, self.tray_icon)
        last_fm_connector.preferences_window = self.pref

        self.restore_state()

        """paly music via arguments"""
        self.play_arguments(sys.argv)
        self.main_window_controller.show()
        """enable proxy"""

        self.check_version()


    def check_version(self):
        uuid = FConfiguration().uuid
        current_version = VERSION
        try:
            f = urllib2.urlopen("http://www.foobnix.com/version?uuid=" + uuid + "&host=" + gethostname())
        except:
            return None

        new_version = f.read()
        LOG.info("versions", current_version , "|", new_version, "|")
        f.close()
        if FConfiguration().check_new_version and current_version < new_version:
            info_dialog_with_link(_("New version is available"), "foobnix " + new_version, "http://www.foobnix.com/?page=download")
            #self.setStatusText(_("New version ")+new_version+_(" avaliable at www.foobnix.com"));


    def action_command(self, args):
        if args:
            if len(args) == 1:
                command = args[0]
            elif len(args) == 2:
                command = args[1]
            else:
                return None
            if "--next" == command:
                self.player_controller.next()
            elif "--prev" == command:
                self.player_controller.prev()
            elif "--stop" == command:
                self.player_controller.stopState()
            elif "--pause" == command:
                self.player_controller.pauseState()
            elif "--play" == command:
                self.player_controller.playState()
            elif "--volume-up" == command:
                self.player_controller.volume_up()
            elif "--volume-down" == command:
                self.player_controller.volume_down()
            elif "--show-hide" == command:
                self.main_window_controller.toggle_visibility()
            elif "--play-pause" == command:
                if self.player_controller.is_state_playing():
                    self.player_controller.pauseState()
                else:
                    self.player_controller.playState()
            return True
        return False

    def play_arguments(self, args):
        #gtk.gdk.threads_leave()
        gtk.gdk.threads_enter() #@UndefinedVariable
        if not self.action_command(args):
            self.main_window_controller.show()
        self.onlineCntr.on_play_argumens(args)
        gtk.gdk.threads_leave()

    def exit(self, *a):
        self.main_window_controller.hide()
        self.save_state()
        gtk.main_quit()

    def restore_state(self):
        if FConfiguration().playlistState:
            self.playlistCntr.setState(FConfiguration().playlistState)

        if FConfiguration().virtualListState:
            self.directoryCntr.setState(FConfiguration().virtualListState)

        if FConfiguration().volumeValue:
            self.playerWidgets.volume.set_value(FConfiguration().volumeValue)
            self.player_controller.setVolume(FConfiguration().volumeValue / 100)

        if FConfiguration().radiolistState:
            self.radioListCntr.setState(FConfiguration().radiolistState)

        if FConfiguration().save_tabs:
            self.onlineCntr.append_notebook_page(FConfiguration().last_notebook_page)

            if FConfiguration().play_on_start:
                self.onlineCntr.append_and_play(FConfiguration().last_notebook_beans, FConfiguration().last_play_bean)
            else:
                self.onlineCntr.append(FConfiguration().last_notebook_beans)


        self.main_window_controller.on_load()




    def save_state(self):
        FConfiguration().last_notebook_page = self.onlineCntr.last_notebook_page
        FConfiguration().last_notebook_beans = self.onlineCntr.last_notebook_beans
        FConfiguration().last_play_bean = self.onlineCntr.index

        FConfiguration().playlistState = self.playlistCntr.getState()
        FConfiguration().virtualListState = self.directoryCntr.getState()

        #FConfiguration().radiolistState = self.radioListCntr.getState()

        FConfiguration().volumeValue = self.playerWidgets.volume.get_value()

        if self.playerWidgets.vpanel.get_position() > 0:
            FConfiguration().vpanelPostition = self.playerWidgets.vpanel.get_position()
        if self.playerWidgets.hpanel.get_position() > 0:
            FConfiguration().hpanelPostition = self.playerWidgets.hpanel.get_position()
        if self.playerWidgets.hpanel.get_position() > 0:
            FConfiguration().hpanel2Postition = self.playerWidgets.hpanel2.get_position()

        self.main_window_controller.on_save()
        FConfiguration().save()

