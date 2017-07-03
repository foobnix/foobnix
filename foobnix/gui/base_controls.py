#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''

import copy
import gi
import os
import logging
import thread
import time

gi.require_version('Notify', '0.7')

from gi.repository import GLib
from gi.repository import Gtk
from gi.repository import Notify
from threading import Lock
from urllib2 import urlopen

from foobnix.fc.fc import FC
from foobnix.fc.fc_base import FCBase
from foobnix.fc.fc_cache import FCache
from foobnix.gui.model import FModel
from foobnix.gui.service.music_service import get_all_music_by_paths
from foobnix.gui.service.vk_service import VKService
from foobnix.gui.state import LoadSave, Quitable
from foobnix.helpers.dialog_entry import file_chooser_dialog, \
    directory_chooser_dialog, info_dialog_with_link_and_donate
from foobnix.util.bean_utils import get_bean_posible_paths
from foobnix.util.const import STATE_PLAY, STATE_PAUSE, STATE_STOP, FTYPE_RADIO
from foobnix.util.file_utils import get_file_extension
from foobnix.util.iso_util import mount_tmp_iso
from foobnix.util.version import compare_versions
from foobnix.util import analytics, idle_task, idle_task_priority
from foobnix.util.text_utils import normalize_text
from foobnix.version import FOOBNIX_VERSION

class BaseFoobnixControls():
    def __init__(self):
        self.vk_service = VKService(FC().access_token, FC().user_id)

        self.count_errors = 0
        self.is_scrobbled = False
        self.start_time = None

        self.cache_text = None
        self.play_lock = Lock()

    def check_for_media(self, args):
        dirs = []
        files = []
        for arg in args:
            if os.path.isdir(arg):
                dirs.append(arg)
            elif os.path.isfile(arg) and get_file_extension(arg) in FC().all_support_formats:
                files.append(arg)
        if dirs:
            self.on_add_folders(dirs)
        elif files:
            self.on_add_files(files)
            try:
                self.play_first_added(files)
            except:
                logging.error("Can't to play first added file")

    def play_first_added(self, added_files):
        tree = self.notetabs.get_current_tree()
        model = tree.get_model()
        number = len(model) - len(added_files)
        if (number) > -1:
            iter = model.get_iter_from_string(str(number))
            bean = tree.get_bean_from_model_iter(model, iter)
            tree.set_play_icon_to_bean(bean)
            self.play(bean)

    def love_this_tracks(self, beans=None):
        if not beans:
            return
        map(self.lastfm_service.love, beans)

    def add_to_my_playlist(self, beans=None):
         if not beans:
             return
         map(self.vk_service.add, beans)

    def copy_link(self, beans=None):
         if not beans:
             return
         if hasattr(beans[0], 'path'):
            cb = Gtk.Clipboard().set_text(beans[0].path)
            cb.store()
            if FC().notifier:
                notification = Notify.Notification.new("In clipboard", beans[0].path, "")
                notification.set_urgency(Notify.Urgency.LOW)
                notification.set_timeout(FC().notify_time)
                notification.show()

    def show_google_results(self, query):
        return [FModel('"%s" not found' % query)]

    def get_active_bean(self):
        tree = self.notetabs.get_current_tree()
        if tree:
            return tree.get_selected_or_current_bean()

    def play_selected_song(self):
        current = self.get_active_bean()
        tree = self.notetabs.get_current_tree()
        if not current:
            try:
                current = tree.get_bean_under_pointer_icon()
            except AttributeError:
                return
        if not current:
            return None
        logging.debug("play current bean is %s" % str(current.text))
        if current and current.is_file:
            tree.set_play_icon_to_bean(current)
            self.play(current)

    def check_path(self, path):
        if path:
            if not path.startswith("http://"):
                if os.path.exists(path):
                    return True
            else:
                try:
                    u = urlopen(path, timeout=5)    # @UnusedVariable
                    if "u" not in vars():
                        return False
                    return True
                except:
                    return False
        return False

    def save_beans_to(self, beans):
        return None

    def on_chage_player_state(self, state, bean):
        logging.debug("bean state %s" % state)

        self.set_dbus_state(state, bean)

        if not FC().system_icons_dinamic:
            return None

        if state == STATE_STOP:
            self.trayicon.set_image_from_path(FC().stop_icon_entry)
        elif state == STATE_PAUSE:
            self.trayicon.set_image_from_path(FC().pause_icon_entry)
        elif state == STATE_PLAY:
            self.trayicon.set_image_from_path(FC().play_icon_entry)

        if bean and bean.type:
            logging.debug("bean state and type %s %s" % (state, bean.type))
            if bean.type == FTYPE_RADIO:
                return self.trayicon.set_image_from_path(FC().radio_icon_entry)

    @idle_task
    def set_dbus_state(self, state, bean):
        if self.dbus:
            self.dbus._update_info(bean)
            if state is STATE_PLAY:
                self.dbus._set_state_play()
            elif state is STATE_PAUSE:
                self.dbus._set_state_pause()
            else:
                self.dbus._set_state_stop()

    def send_track_changed_signal_to_dbus(self, bean):
        if self.dbus:
            if not bean.info:
                bean.info ="no technical info available"
            self.dbus.player.current(bean.text, bean.info)

    def on_add_folders(self, paths=None):
        if not paths:
            paths = directory_chooser_dialog(_("Choose folders to open"), FC().last_dir)
            if not paths:
                return
        tree = self.notetabs.get_current_tree()
        FC().last_dir = os.path.dirname(paths[0])
        if tree.is_empty():
            if len(paths) > 1:
                tabname = os.path.basename(FC().last_dir)
            else:
                tabname = os.path.basename(paths[0])
            self.notetabs.rename_tab(tree.scroll, tabname)
        tree.append(paths)

    def on_add_files(self, paths=None, tab_name=None):
        if not paths:
            paths = file_chooser_dialog(_("Choose file to open"), FC().last_dir)
            if not paths:
                return
        tree = self.notetabs.get_current_tree()
        FC().last_dir = os.path.dirname(paths[0])
        if tree.is_empty():
            tabname = os.path.split(os.path.dirname(paths[0]))[1]
            self.notetabs.rename_tab(tree.scroll, tabname)
        tree.append(paths)

    def set_playlist_tree(self):
        self.notetabs.set_playlist_tree()

    def set_playlist_plain(self):
        self.notetabs.set_playlist_plain()

    def load_music_tree(self):
        tabs = len(FCache().cache_music_tree_beans)
        tabhelper = self.perspectives.get_perspective('fs').get_tabhelper()
        for tab in xrange(tabs - 1, -1, -1):
            tabhelper._append_tab(FCache().tab_names[tab], rows=FCache().cache_music_tree_beans[tab])

            if not FCache().cache_music_tree_beans[tab]:
                self.perspectives.get_perspective('fs').show_add_button()
            else:
                self.perspectives.get_perspective('fs').hide_add_button()

            logging.info("Tree loaded from cache")

        if FC().update_tree_on_start:
            def cycle():
                for n in xrange(len(FCache().music_paths)):
                    tab_child = tabhelper.get_nth_page(n)
                    tree = tab_child.get_child()
                    self.update_music_tree(tree, n)
            GLib.idle_add(cycle)

    def update_music_tree(self, tree, number_of_page=0):
        logging.info("Update music tree" + str(FCache().music_paths[number_of_page]))
        tree.clear_tree()   # safe method
        FCache().cache_music_tree_beans[number_of_page] = {}

        all = get_all_music_by_paths(FCache().music_paths[number_of_page], self)

        try:
            self.perspectives.get_perspective('fs').hide_add_button()
        except AttributeError:
            logging.warn("Object perspective not exists yet")

        if not all:
            try:
                self.perspectives.get_perspective('fs').show_add_button()
            except AttributeError:
                logging.warn("Object perspective not exists yet")
        tree.append_all(all)     # safe method
        tree.ext_width = tree.ext_column.get_width()

        GLib.idle_add(tree.save_rows_from_tree,
                         FCache().cache_music_tree_beans[number_of_page])
        #GLib.idle_add(self.tabhelper.on_save_tabs)   # for true order

    @idle_task
    def set_visible_video_panel(self, flag):
        return
        #FC().is_view_video_panel = flag
        #if flag:
        #    self.movie_window.show()
        #else:
        #    self.movie_window.hide()

    @idle_task
    def volume_up(self):
        self.volume.volume_up()

    @idle_task
    def volume_down(self):
        self.volume.volume_down()

    @idle_task
    def mute(self):
        self.volume.mute()

    @idle_task
    def hide(self):
        self.main_window.hide()

    @idle_task
    def show_hide(self):
        self.main_window.show_hide()

    @idle_task
    def show(self):
        self.main_window.show()

    @idle_task
    def play_pause(self):
        if self.media_engine.get_state() == STATE_PLAY:
            self.media_engine.state_pause()
        elif self.media_engine.get_state() == STATE_STOP:
            self.state_play(True)
        else:
            self.media_engine.state_play()

    @idle_task
    def seek_up(self):
        self.media_engine.seek_up()

    @idle_task
    def seek_down(self):
        self.media_engine.seek_down()

    @idle_task
    def windows_visibility(self):
        visible = self.main_window.get_property('visible')
        if visible:
            GLib.idle_add(self.main_window.hide)
        else:
            GLib.idle_add(self.main_window.show)

    @idle_task
    def state_play(self, under_pointer_icon=False):
        if self.media_engine.get_state() == STATE_PAUSE:
            self.media_engine.state_play()
            self.statusbar.set_text(self.media_engine.bean.info)
        elif under_pointer_icon:
            tree = self.notetabs.get_current_tree()
            bean = tree.get_bean_under_pointer_icon()
            self.play(bean)
        else:
            self.play_selected_song()

    @idle_task
    def show_preferences(self):
        if not self.preferences.get_property("visible"):  # checking to avoid reset pref. window item to first
            self.preferences.show()

    @idle_task
    def state_pause(self):
        self.media_engine.state_pause()

    @idle_task_priority(priority=GLib.PRIORITY_HIGH_IDLE)
    def state_stop(self, remember_position=False):
        self.record.hide()
        self.media_engine.state_stop(remember_position)
        if not remember_position:
            self.statusbar.set_text(_("Stopped"))
            self.seek_bar.clear()

    @idle_task
    def state_play_pause(self):
        self.media_engine.state_play_pause()
        bean = self.media_engine.bean
        if self.media_engine.get_state() == STATE_PLAY:
            self.statusbar.set_text(bean.info)
        else:
            self.statusbar.set_text(_("Paused | ") + str(bean.info))

    def state_is_playing(self):
        return self.media_engine.get_state() == STATE_PLAY

    def fill_bean_from_vk(self, bean):
        if bean.type and bean.type == FTYPE_RADIO:
            return False
        vk = self.vk_service.find_one_track(bean.get_display_name())
        if vk:
            bean.path = vk.path
            bean.time = vk.time
            return True
        else:
            return False

    def fill_bean_by_vk_aid(self, bean):
        if not bean.vk_audio_id:
            return False
        if bean.type and bean.type == FTYPE_RADIO:
            return False
        track = self.vk_service.find_track_by_id(bean.vk_audio_id)
        if track:
            bean.path = track.path
            bean.time = track.time
            return True
        return False

    @idle_task
    def play(self, bean):
        if not bean or not bean.is_file:
            return

        self.play_lock.acquire()
        self.seek_bar.clear()
        ## TODO: Check for GTK+3.4 (Status icon doesn't have a set_tooltip method)

        self.statusbar.set_text(bean.info)
        self.trayicon.set_text(bean.text)
        self.send_track_changed_signal_to_dbus(bean)
        #self.movie_window.set_text(bean.text)

        if bean.type == FTYPE_RADIO:
            self.record.show()
            self.seek_bar.progressbar.set_fraction(0)
            self.seek_bar.set_text(_("Radio ") + bean.text.capitalize())
        else:
            self.record.hide()

        self.main_window.set_title(bean.text)

        thread.start_new_thread(self._one_thread_play, (bean,))

    def _one_thread_play(self, bean):
        try:
            self._play(bean)
        finally:
            if self.play_lock.locked():
                self.play_lock.release()

    def _play(self, bean):
        if not bean.path:
            bean.path = get_bean_posible_paths(bean)

        if not self.check_path(bean.path):
            if bean.iso_path and os.path.exists(bean.iso_path):
                logging.info("Try to remount " + bean.iso_path)
                mount_tmp_iso(bean.iso_path)
            elif bean.vk_audio_id:
                self.fill_bean_by_vk_aid(bean)
            elif not bean.path or ("userapi" in bean.path) or ("vk.me" in bean.path):
                self.fill_bean_from_vk(bean)
            else:
                resource = bean.path if bean.path else bean.text
                logging.error("Resourse " + resource + " not found")
                self.media_engine.state_stop(show_in_tray=False)
                self.statusbar.set_text(_("Resource not found"))
                self.seek_bar.set_text(_("Resource not found"))
                self.count_errors += 1
                time.sleep(2)
                if self.count_errors < 4:
                    if self.play_lock.locked():
                        self.play_lock.release()
                    self.next()
                else:
                    self.seek_bar.set_text(_("Stopped. No resources found"))
                return

        elif os.path.isdir(bean.path):
            return

        self.count_errors = 0
        self.media_engine.play(bean)
        self.is_scrobbled = False
        self.start_time = False

        if bean.type != FTYPE_RADIO:
            self.update_info_panel(bean)
        self.set_visible_video_panel(False)

    @idle_task
    def notify_playing(self, pos_sec, dur_sec, bean):
        if not bean.type or bean.type != FTYPE_RADIO:
            self.seek_bar.update_seek_status(pos_sec, dur_sec)
        else:
            self.seek_bar.fill_seekbar()

        if pos_sec == 2 or (pos_sec > 2 and (pos_sec % 20) == 0):
            self.net_wrapper.execute(self.lastfm_service.report_now_playing, bean)

        if not self.start_time:
            self.start_time = str(int(time.time()))

        if not self.is_scrobbled and bean.type != FTYPE_RADIO:
            ## song should be scrobbled if 90% has been played or played greater than 5 minutes
            if pos_sec > (dur_sec * 0.5) or pos_sec > (60 * 2):
                self.is_scrobbled = True
                self.net_wrapper.execute(self.lastfm_service.report_scrobbled, bean, self.start_time, dur_sec)
                """download music"""
                if FC().automatic_online_save and bean.path and bean.path.startswith("http://"):
                    self.dm.append_task(bean)

    @idle_task
    def notify_title(self, bean, raw_text):
        logging.debug("Notify title: " + raw_text)
        text = raw_text.partition("||")[0]
        if not self.cache_text:
            self.cache_text = text

        self.statusbar.set_text(raw_text.replace("||", "|"))

        text = normalize_text(text)

        self.seek_bar.set_text(text)
        t_bean = bean.create_from_text(text)
        self.update_info_panel(t_bean)
        self.set_dbus_state(STATE_PLAY, t_bean)
        if FC().enable_radio_scrobbler and bean.type == FTYPE_RADIO:
            start_time = str(int(time.time()))
            self.net_wrapper.execute(self.lastfm_service.report_now_playing, t_bean)

            if " - " in text and self.cache_text != text:
                c_bean = copy.copy(bean)
                prev_bean = c_bean.create_from_text(self.cache_text)
                self.net_wrapper.execute(self.lastfm_service.report_scrobbled, prev_bean, start_time, 200)
                self.cache_text = text

    @idle_task
    def notify_error(self, msg):
        logging.error("notify error " + msg)
        self.seek_bar.set_text(msg)
        self.perspectives.get_perspective('info').clear()

    @idle_task
    def notify_eos(self):
        self.next()

    @idle_task
    def player_seek(self, percent):
        self.media_engine.seek(percent)

    @idle_task
    def player_seek_microseconds(self, time_us, offset=0.0):
        percent = 100.0 * (offset + time_us) / self.duration_microseconds
        if percent > 100.0:
            percent = 100.0
        elif percent < 0.0:
            percent = 0.0
        self.player_seek(percent)

    @idle_task
    def player_seek_microseconds_relative(self, time_us):
        self.player_seek_microseconds(time_us, offset=self.position_microseconds)

    @idle_task
    def player_volume(self, percent):
        self.media_engine.volume(percent)
        self.volume.set_value(percent)

    def get_player_volume(self):
        return self.volume.get_value()

    def search_vk_page_tracks(self, vk_ulr):
        logging.debug("Search vk_service page tracks")
        results = self.vk_service.find_tracks_by_url(vk_ulr)
        all = []
        p_bean = FModel(vk_ulr).add_font("bold")
        all.append(p_bean)
        for i, bean in enumerate(results):
            bean.tracknumber = i + 1
            bean.parent(p_bean).add_is_file(True)
            all.append(bean)

        self.notetabs.append_tab(vk_ulr, all)

    def search_all_tracks(self, query):
        def search_all_tracks_task():
            analytics.action("SEARCH_search_all_tracks")
            results = self.vk_service.find_tracks_by_query(query)
            if not results:
                results = []
            all = []
            p_bean = FModel(query).add_font("bold")
            all.append(p_bean)
            for i, bean in enumerate(results):
                bean.tracknumber = i + 1
                bean.parent(p_bean).add_is_file(True)
                all.append(bean)

            if not results:
                all = self.show_google_results(query)

            self.notetabs.append_tab(query, all)
        self.in_thread.run_with_spinner(search_all_tracks_task, no_thread=True)

    def search_top_tracks(self, query):
        def search_top_tracks_task(query):
            analytics.action("SEARCH_search_top_tracks")
            results = self.lastfm_service.search_top_tracks(query)
            if not results:
                results = []
            all = []
            parent_bean = FModel(query)
            all.append(parent_bean)
            for i, bean in enumerate(results):
                bean.tracknumber = i + 1
                bean.parent(parent_bean).add_is_file(True)
                all.append(bean)

            if not results:
                all = self.show_google_results(query)

            self.notetabs.append_tab(query, all)

        self.in_thread.run_with_spinner(search_top_tracks_task, query)

    def search_top_albums(self, query):
        def search_top_albums_task(query):
            analytics.action("SEARCH_search_top_albums")
            results = self.lastfm_service.search_top_albums(query)
            if not results:
                results = []
            self.notetabs.append_tab(query, None)
            albums_already_inserted = []
            for album in results[:15]:
                all = []
                if album.album.lower() in albums_already_inserted:
                    continue
                album.is_file = False
                tracks = self.lastfm_service.search_album_tracks(album.artist, album.album)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    track.album = album.album
                    track.year = album.year
                    track.parent(album).add_is_file(True)
                    all.append(track)
                if len(all) > 0:
                    all = [album] + all
                    albums_already_inserted.append(album.album.lower())
                    self.notetabs.append_all(all)

            if not results:
                all = self.show_google_results(query)
                self.notetabs.append_all(all)

        self.in_thread.run_with_spinner(search_top_albums_task, query)

    def search_top_similar(self, query):

        def search_top_similar_task(query):
            analytics.action("SEARCH_search_top_similar")
            results = self.lastfm_service.search_top_similar_artist(query)
            if not results:
                results = []
            self.notetabs.append_tab(query, None)
            for artist in results[:15]:
                all = []
                artist.is_file = False
                all.append(artist)
                tracks = self.lastfm_service.search_top_tracks(artist.artist)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    track.parent(artist).add_is_file(True)
                    all.append(track)

                self.notetabs.append_all(all)

            if not results:
                all = self.show_google_results(query)

        #inline(query)
        self.in_thread.run_with_spinner(search_top_similar_task, query)

    def search_top_tags(self, query):

        def search_top_tags_task(query):
            analytics.action("SEARCH_search_top_tags")
            results = self.lastfm_service.search_top_tags(query)
            if not results:
                logging.debug("tag result not found")
                results = []
            self.notetabs.append_tab(query, None)
            for tag in results[:15]:
                all = []
                tag.is_file = False
                all.append(tag)
                tracks = self.lastfm_service.search_top_tag_tracks(tag.text)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    track.parent(tag).add_is_file(True)
                    all.append(track)

                self.notetabs.append_all(all)

            if not results:
                all = self.show_google_results(query)
                self.notetabs.append_all(all)

        #inline(query)
        self.in_thread.run_with_spinner(search_top_tags_task, query)

    @idle_task
    def update_info_panel(self, bean):
        self.perspectives.get_perspective('info').update(bean)

    @idle_task
    def append_to_new_notebook(self, text, beans, optimization=False):
        self.notetabs._append_tab(text, beans, optimization)

    @idle_task
    def append_to_current_notebook(self, beans):
        self.notetabs.append_all(beans)

    @idle_task
    def next(self):
        bean = self.notetabs.next()
        if not bean:
            return
        gap = FC().gap_secs
        time.sleep(gap)
        logging.debug("play current bean is %s" % str(bean.text))

        self.play(bean)

    @idle_task
    def prev(self):
        bean = self.notetabs.prev()
        if not bean:
            return

        self.play(bean)

    def quit(self, *a):
        self.state_stop()

        self.main_window.hide()
        self.trayicon.hide()

        logging.info("Controls - Quit")

        for element in self.__dict__:
            if isinstance(self.__dict__[element], Quitable):
                self.__dict__[element].on_quit()

        FC().save()

        GLib.idle_add(Gtk.main_quit) # wait for complete stop task

    def check_version(self):
        uuid = FCBase().uuid
        current_version = FOOBNIX_VERSION
        system = "not_set"
        try:
            import platform
            system = platform.system()
        except:
            pass

        try:
            from socket import gethostname
            f = urlopen("http://www.foobnix.com/version?uuid=" + uuid + "&host=" + gethostname()
                        + "&version=" + current_version + "&platform=" + system, timeout=7)
            #f = urllib2.urlopen("http://localhost:8080/version?uuid=" + uuid + "&host=" + gethostname() + "&v=" + current_version)
        except Exception as e:
            logging.error("Check version error: " + str(e))
            return None

        new_version_line = f.read()

        logging.info("version " + current_version + "|" + new_version_line + "|" + str(uuid))

        f.close()
        if FC().check_new_version and compare_versions(current_version, new_version_line) == 1:
            info_dialog_with_link_and_donate(new_version_line)

    def on_load(self):
        """load controls"""
        for element in self.__dict__:
            if isinstance(self.__dict__[element], LoadSave):
                init = time.time()
                self.__dict__[element].on_load()
                logging.debug("%f LOAD ON START %s" % (time.time() - init, "Instance of " + self.__dict__[element].__class__.__name__))

        """load others"""
        #self.movie_window.hide_all()

        self.main_window.show()
        self.search_progress.stop()

        """base layout"""
        self.layout.on_load()

        """check for new version"""

        if os.name == 'nt':
            self.check_version()
        else:
            pass
            #GLib.idle_add(self.check_version)

    @idle_task_priority(GLib.PRIORITY_LOW)
    def play_first_file_in_playlist(self):
        active_playlist_tree = self.notetabs.get_current_tree()
        filter_model = active_playlist_tree.get_model()
        current_model = filter_model.get_model()

        def play_item(iter, active_playlist_tree, filter_model, current_model):
            bean = active_playlist_tree.get_bean_from_model_iter(current_model, iter)
            if not bean:
                return

            if bean.font != 'bold':
                self.play(bean)
                tree_selection = active_playlist_tree.get_selection()
                filter_iter = filter_model.convert_child_iter_to_iter(iter)
                if filter_iter[0]:
                    GLib.idle_add(tree_selection.select_iter, filter_iter[1])
                active_playlist_tree.set_play_icon_to_bean_to_selected()
            else:
                iter = current_model.iter_next(iter)
                play_item(iter, active_playlist_tree, filter_model, current_model)

        iter = current_model.get_iter_first()
        play_item(iter, active_playlist_tree, filter_model, current_model)

    def on_save(self):
        for element in self.__dict__:
            if isinstance(self.__dict__[element], LoadSave):
                logging.debug("SAVE " + str(self.__dict__[element]))
                self.__dict__[element].on_save()

    def download(self):
        self.dm.append_task(bean=self.notetabs.get_current_tree().get_current_bean_by_UUID())

    @property
    def position_microseconds(self):
        return self.media_engine.position_sec * 1000000

    @property
    def duration_microseconds(self):
        return self.media_engine.duration_sec * 1000000
