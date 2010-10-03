#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.util.fc import FC
from foobnix.util import LOG
from foobnix.regui.state import LoadSave
from foobnix.regui.treeview.scanner import DirectoryScanner
from foobnix.regui.id3 import update_all_id3
import os
from foobnix.regui.model import FModel
from foobnix.regui.service.lastfm_service import LastFmService
from foobnix.util.singe_thread import SingreThread
from foobnix.regui.service.vk_service import VKService
from foobnix.util.plsparser import get_radio_source
from foobnix.radio.radios import RadioFolder

class BaseFoobnixControls(LoadSave):
    def __init__(self):
        self.lastfm = LastFmService()
        self.vk = VKService()

        self.count_errors = 0

        self.is_radio_populated = False
        pass

    def load_music_tree(self):
        if FC().cache_music_tree_beans:
            self.tree.populate_from_scanner(FC().cache_music_tree_beans)
            LOG.info("Tree loaded from cache")
        else:
            self.update_music_tree()
            LOG.info("Tree updated")

    def update_music_tree(self):
        LOG.info("Update music tree", FC().music_paths)
        self.tree.clear()
        FC().cache_music_tree_beans = []
        for path in FC().music_paths:
            scan = DirectoryScanner(path)
            all = scan.get_music_results()

            for bean in all:
                FC().cache_music_tree_beans.append(bean)

            self.tree.append_from_scanner(all)




    def update_radio_tree(self):
        if self.is_radio_populated:
            return True
        LOG.info("Update radio tree")
        self.radio_folder = RadioFolder()
        files = self.radio_folder.get_radio_FPLs()
        for fpl in files:
            parent = FModel(fpl.name).add_font("bold").add_is_file(False)
            parentIter = self.radio.append(parent)
            for radio, urls in fpl.urls_dict.iteritems():
                child = FModel(radio, urls[0]).add_font("").add_level(parentIter).add_is_file(True)
                self.radio.append(child)
        self.is_radio_populated = True

    def set_visible_search_panel(self, flag):
        self.layout.set_visible_search_panel(flag)

    def set_visible_musictree_panel(self, flag):
        self.layout.set_visible_musictree_panel(flag)

    def set_visible_info_panel(self, flag):
        self.layout.set_visible_info_panel(flag)

    def volume_up(self):
        pass

    def volume_down(self):
        pass

    def windows_visibility(self):
        visible = self.main_window.get_property('visible')
        if visible:
            self.main_window.hide()
        else:
            self.main_window.show()

    def state_play(self):
        self.media_engine.state_play()

    def show_preferences(self):
        self.preferences.show()

    def state_pause(self):
        self.media_engine.state_pause()

    def state_stop(self):
        self.media_engine.state_stop()

    def state_play_pause(self):
        self.media_engine.state_play_pause()

    def play(self, bean):
        if not bean.path:
            vk = self.vk.find_one_track(bean.artist + " - " + bean.title)
            if vk:
                bean.path = vk.path
                bean.time = vk.time
            else:
                if self.count_errors < 4:
                    self.next()
                self.count_errors += 1
        else:
            bean.path = get_radio_source(bean.path)


        self.media_engine.play(bean)

        print "!!!!!!", bean.info
        self.count_errors = 0
        self.statusbar.set_text(bean.info)
        self.trayicon.set_text(bean.text)

    def notify_playing(self, pos_sec, dur_sec):
        self.seek_bar.update_seek_status(pos_sec, dur_sec)

    def notify_title(self, text):
        self.seek_bar.set_text(text)

    def notify_eos(self):
        self.next()

    def player_seek(self, percent):
        self.media_engine.seek(percent)

    def player_volue(self, percent):
        self.media_engine.volume(percent)

    def search_top_tracks(self, query):
        def inline(query):
            results = self.lastfm.search_top_tracks(query)
            all = []
            all.append(FModel(query).add_font("bold"))
            for i, bean in enumerate(results):
                bean.tracknumber = i + 1
                all.append(bean)
            self.notetabs.append_tab(query, all)
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)



    def search_top_albums(self, query):
        def inline(query):
            results = self.lastfm.search_top_albums(query)
            self.notetabs.append_tab(query, None)
            for album in results[:5]:
                all = []
                album.add_font("bold")
                all.append(album)
                tracks = self.lastfm.search_album_tracks(album.artist, album.album)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    all.append(track)
                self.notetabs.append(all)
        #inline(query)
        #self.singre_thread.run(inline, query)
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)

    def search_top_similar(self, query):
        def inline(query):
            results = self.lastfm.search_top_similar_artist(query)
            self.notetabs.append_tab(query, None)
            for artist in results[:5]:
                all = []
                artist.add_font("bold")
                all.append(artist)
                tracks = self.lastfm.search_top_tracks(artist.artist)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    all.append(track)
                self.notetabs.append(all)
        #inline(query)
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)

    def search_top_tags(self, query):
        def inline(query):
            results = self.lastfm.search_top_tags(query)
            self.notetabs.append_tab(query, None)
            for tag in results[:5]:
                all = []
                tag.add_font("bold")
                all.append(tag)
                tracks = self.lastfm.search_top_tag_tracks(tag.text)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    all.append(track)
                self.notetabs.append(all)
        #inline(query)
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)

    def search_all(self, query):
        pass
        def inline(query):
            print query
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)

    def update_info_panel(self, bean):
        #self.info_panel.update(bean)
        self.singre_thread.run_with_text(self.info_panel.update, bean, "Updating info panel")

    def append_to_new_notebook(self, text, beans):
        path = beans[0].path
        if os.path.isdir(path):
            scanner = DirectoryScanner(beans[0].path)
            results = scanner.get_music_file_results()
            results = update_all_id3(results)
            self.notetabs.append_tab(text, results)
        else:
            self.notetabs.append_tab(text, [beans[0]])

    def append_to_current_notebook(self, beans):
        bean = beans[0]
        if bean.is_file:
            self.notetabs.append([beans[0]])
        else:
            scanner = DirectoryScanner(beans[0].path)
            results = scanner.get_music_file_results()
            results = update_all_id3(results)
            self.notetabs.append(results)


    def next(self):
        bean = self.notetabs.next()
        self.play(bean)

    def prev(self):
        bean = self.notetabs.prev()
        self.play(bean)

    def filter_tree(self, value):
        self.tree.filter(value)
        self.radio.filter(value)

    def quit(self, *a):
        LOG.info("Controls - Quit")
        self.on_save()
        FC().save()

        gtk.main_quit()

    def set_playback_random(self, flag):
        self.notetabs.set_random(flag)

    def on_load(self):
        for element in self.__dict__:
            if isinstance(self.__dict__[element], LoadSave):
                self.__dict__[element].on_load()
            else:
                LOG.debug("NOT LOAD", self.__dict__[element])
        self.singre_thread = SingreThread(self.search_progress)
        self.main_window.show()

    def on_save(self):
        for element in self.__dict__:
            if isinstance(self.__dict__[element], LoadSave):
                self.__dict__[element].on_save()
            else:
                LOG.debug("NOT SAVE", self.__dict__[element])
