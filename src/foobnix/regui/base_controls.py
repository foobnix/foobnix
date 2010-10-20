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
from foobnix.regui.model import FModel
from foobnix.regui.service.lastfm_service import LastFmService
from foobnix.util.singe_thread import SingreThread
from foobnix.regui.service.vk_service import VKService
from foobnix.util.plsparser import get_radio_source
from foobnix.radio.radios import RadioFolder
from foobnix.helpers.dialog_entry import file_chooser_dialog, \
    directory_chooser_dialog
from foobnix.regui.service.music_service import get_all_music_by_path
from foobnix.regui.id3 import update_id3_wind_filtering

class BaseFoobnixControls(LoadSave):
    def __init__(self):
        self.lastfm = LastFmService()
        self.vk = VKService()

        self.count_errors = 0

        self.is_radio_populated = False
        pass
    
   
    def on_add_folders(self):
        paths = directory_chooser_dialog("Choose folders to open", FC().last_dir)
        if paths:
            path = paths[0]
            list = path.split("/")
            FC().last_dir = path[:path.rfind("/")]
            name = list[len(list) - 1]
            parent = FModel(name)
            self.append_to_new_notebook(name, [])
    
            all_beans = []
            all_beans.append(parent)
            for path in paths:
                if path == "/":
                    LOG.info("Skip root folder")
                    continue;
                beans = get_all_music_by_path(path)
                
                for bean in beans:
                    if not bean.is_file:
                        bean.parent(parent).add_is_file(False)
                    all_beans.append(bean)
    
            if all_beans:
                self.append_to_current_notebook(all_beans)
            else:
                self.append([self.SearchCriteriaBeen(_("Nothing found to play in the folder(s)") + paths[0])])
    
    def on_add_files(self):       
        paths = file_chooser_dialog("Choose file to open", FC().last_dir)
        if paths:            
            path = paths[0]
            list = paths[0].split("/")
    
            FC().last_dir = path[:path.rfind("/")]
            
            name = list[len(list) - 2]
            self.append_to_new_notebook(name, [])
            parent = FModel(name)
            self.append_to_current_notebook([parent])
            beans = []
            for path in paths:
                bean = FModel(path, path).parent(parent)
                beans.append(bean)
            if not beans:
                self.append_to_current_notebook([FModel("Nothing found to play in the file(s) " + paths[0])])
            else:
                self.append_to_current_notebook(beans)
       
    def set_playlist_tree(self):
        self.notetabs.set_playlist_tree()

    def set_playlist_plain(self):
        self.notetabs.set_playlist_plain()

    def load_music_tree(self):
        if FC().cache_music_tree_beans:
            self.tree.append_all(FC().cache_music_tree_beans)
            LOG.info("Tree loaded from cache")
        else:
            self.update_music_tree()
            LOG.info("Tree updated")

    def update_music_tree(self):
        LOG.info("Update music tree", FC().music_paths)
        self.tree.clear()
        FC().cache_music_tree_beans = []
        for path in FC().music_paths:
            
            all = get_all_music_by_path(path)

            for bean in all:
                FC().cache_music_tree_beans.append(bean)

            self.tree.append_all(all)

    def update_radio_tree(self):
        if self.is_radio_populated:
            return True
        LOG.info("Update radio tree")
        self.radio_folder = RadioFolder()
        files = self.radio_folder.get_radio_FPLs()
        for fpl in files:
            print fpl, fpl.name
            parent = FModel(fpl.name).add_is_file(False)
            self.radio.append(parent)
            for radio, urls in fpl.urls_dict.iteritems():
                child = FModel(radio, urls[0]).parent(parent)
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

    def fill_bean_from_vk(self, bean):
        if not bean.artist or not bean.title:
            vk = self.vk.find_one_track(" - ".join([x for x in [bean.artist, bean.title] if x]))
        else:
            vk = self.vk.find_one_track(bean.text)
        if vk:
            bean.path = vk.path
            bean.time = vk.time
            return True
        else:
            return False

    def play(self, bean):
        if not bean:
            return None

        if not bean.path:
            if not self.fill_bean_from_vk(bean):
                if self.count_errors < 4:
                    self.next()
                self.count_errors += 1
        else:
            bean.path = get_radio_source(bean.path)

        
        self.media_engine.play(bean)
        
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

    def search_all_tracks(self, query):
        def inline(query):
            results = self.vk.find_tracks_by_query(query)
            all = []
            p_bean = FModel(query).add_font("bold")
            all.append(p_bean)
            for i, bean in enumerate(results):
                bean.tracknumber = i + 1
                bean.parent(p_bean)
                all.append(bean)
            self.notetabs.append_tab(query, all)
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)

    def search_top_tracks(self, query):
        def inline(query):
            results = self.lastfm.search_top_tracks(query)
            all = []
            parent_bean = FModel(query)
            all.append(parent_bean)
            for i, bean in enumerate(results):
                bean.tracknumber = i + 1
                bean.parent(parent_bean)                
                all.append(bean)
            self.notetabs.append_tab(query, all)
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)



    def search_top_albums(self, query):
        def inline(query):
            results = self.lastfm.search_top_albums(query)
            self.notetabs.append_tab(query, None)
            for album in results[:5]:
                all = []
                album.is_file = False
                all.append(album)
                tracks = self.lastfm.search_album_tracks(album.artist, album.album)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    track.parent(album)                    
                    all.append(track)
                self.notetabs.append(all)                       
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)

    def search_top_similar(self, query):
        def inline(query):
            results = self.lastfm.search_top_similar_artist(query)
            self.notetabs.append_tab(query, None)
            for artist in results[:5]:
                all = []
                artist.is_file = False
                all.append(artist)
                tracks = self.lastfm.search_top_tracks(artist.artist)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    track.parent(artist)
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
                tag.is_file = False
                all.append(tag)
                tracks = self.lastfm.search_top_tag_tracks(tag.text)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    track.parent(tag)
                    all.append(track)
                self.notetabs.append(all)
        #inline(query)
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)

    def update_info_panel(self, bean):
        #self.info_panel.update(bean)
        self.singre_thread.run_with_text(self.info_panel.update, bean, "Updating info panel")

    def append_to_new_notebook(self, text, beans):
        beans = update_id3_wind_filtering(beans)        
        self.notetabs.append_tab(text, beans)

    def append_to_current_notebook(self, beans):  
        beans = update_id3_wind_filtering(beans)              
        self.notetabs.append(beans)


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

    def set_lopping_all(self):
        self.notetabs.set_lopping_all()

    def set_lopping_single(self):
        self.notetabs.set_lopping_single()

    def set_lopping_disable(self):
        self.notetabs.set_lopping_disable()

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
