#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.util.fc import FC
from foobnix.util import LOG
from foobnix.regui.state import LoadSave
from foobnix.regui.model import FModel
from foobnix.regui.service.lastfm_service import LastFmService
from foobnix.util.singe_thread import SingreThread
from foobnix.regui.service.vk_service import VKService
from foobnix.util.plsparser import get_radio_source
from foobnix.helpers.dialog_entry import file_chooser_dialog, \
    directory_chooser_dialog, info_dialog_with_link
from foobnix.regui.service.music_service import get_all_music_by_path
from foobnix.regui.id3 import update_id3_wind_filtering
import os
import time
from foobnix.regui.service.google_service import google_search_resutls
from foobnix.util.file_utils import get_file_extenstion
from foobnix.util.const import STATE_PLAY, STATE_PAUSE
import urllib2
from foobnix.util.configuration import VERSION

class BaseFoobnixControls(LoadSave):
    def __init__(self):
        self.lastfm = LastFmService()
        self.vk = VKService()

        self.count_errors = 0
        self.is_scrobled = False
        self.start_time = None
        
    def check_for_media(self, args):         
        dirs = []
        files = []
        for arg in args:            
            if os.path.isdir(arg):
                dirs.append(arg)
            elif os.path.isfile(arg) and get_file_extenstion(arg) in FC().support_formats:
                files.append(arg)
        if dirs:
            self.on_add_folders(dirs)
        elif files:            
            self.on_add_files(files)
    
    def show_google_results(self, query):
        beans = []
        beans.append(FModel('"%s" not found try Google results' % query))
        g_results = google_search_resutls(query)
        for line in g_results:
            beans.append(FModel(line).add_is_file(True))
        return beans
    
    def play_selected_song(self):    
        current = self.notetabs.get_active_tree().get_selected_bean()
        if current.is_file:
            self.notetabs.get_active_tree().set_play_icon_to_bean_to_selected()
        
        """play song"""
        self.play(current)

        """set active tree"""
        #self.notetabs.switch_tree(self)
    
    def save_beans_to(self, beans):
        return None    
   
    def on_add_folders(self, paths=None):
        if not paths:
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
    
    def on_add_files(self, paths=None):
        if not paths:       
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

    def set_visible_search_panel(self, flag):
        self.layout.set_visible_search_panel(flag)

    def set_visible_musictree_panel(self, flag):
        self.layout.set_visible_musictree_panel(flag)

    def set_visible_info_panel(self, flag):
        FC().is_view_info_panel = flag
        self.layout.set_visible_info_panel(flag)
        
    def set_visible_video_panel(self, flag):
        FC().is_view_video_panel = flag
        if flag:
            self.movie_window.show()
        else:
            self.movie_window.hide()

    def volume_up(self):
        self.volume.volume_up()

    def volume_down(self):
        self.volume.volume_down()
    
    def show_hide(self):
        self.main_window.show_hide()
    
    def play_pause(self):
        print self.media_engine.get_state()        
        if self.media_engine.get_state() == STATE_PLAY:
            self.media_engine.state_pause()            
        else:
            self.media_engine.state_play()
            
    
    def windows_visibility(self):
        visible = self.main_window.get_property('visible')
        if visible:
            self.main_window.hide()
        else:
            self.main_window.show()

    def state_play(self):
        if self.media_engine.get_state() == STATE_PAUSE:
            self.media_engine.state_play()
        else:
            self.play_selected_song()
        
    
    def show_preferences(self):
        self.preferences.show()

    def state_pause(self):
        self.media_engine.state_pause()

    def state_stop(self):
        self.media_engine.state_stop()

    def state_play_pause(self):
        self.media_engine.state_play_pause()

    def fill_bean_from_vk(self, bean):
        vk = self.vk.find_one_track(bean.get_display_name())
        if vk:
            bean.path = vk.path
            bean.time = vk.time
            return True
        else:
            return False

    def play(self, bean):
        if not bean:
            return None
        
        if not bean.is_file:
            return None
        
        if not bean.path:
            if not self.fill_bean_from_vk(bean):
                if self.count_errors < 4:
                    self.next()
                self.count_errors += 1
        else:
            bean.path = get_radio_source(bean.path)
            
        self.is_scrobled = False
        self.start_time = False
        
        self.seek_bar.clear()
        self.count_errors = 0
        self.statusbar.set_text(bean.info)
        self.trayicon.set_text(bean.text)
        self.main_window.set_title(bean.text)
        
        self.media_engine.play(bean)        

        
        #print "updation info panel"
        self.update_info_panel(bean)

    def notify_playing(self, pos_sec, dur_sec, bean):
        self.seek_bar.update_seek_status(pos_sec, dur_sec)
                        
        if int(pos_sec) % 10 == 0:
            self.lastfm.report_now_playting(bean)
            
        if not self.start_time:
            self.start_time = str(int(time.time()))
            print "Start time", self.start_time

        if not self.is_scrobled  and (pos_sec >= dur_sec / 2 or (pos_sec >= 45)):
            self.lastfm.report_scrobled(bean, self.start_time, dur_sec)
            self.is_scrobled = True
            
                
            

    def notify_title(self, text):
        self.seek_bar.set_text(text)       
        t_bean = FModel(text).create_from_text(text)                       
        self.update_info_panel(t_bean)
    
    def notify_error(self, msg):
        print "notify error"
        self.seek_bar.set_text(msg)
        self.info_panel.clear()
        
    def notify_eos(self):
        self.start_time = None
        self.is_scrobled = False
        self.next()

    def player_seek(self, percent):
        self.media_engine.seek(percent)

    def player_volue(self, percent):
        self.media_engine.volume(percent)
        

    def search_vk_page_tracks(self, vk_ulr):
        def inline(vk_ulr):
            results = self.vk.find_tracks_by_url(vk_ulr)
            all = []
            p_bean = FModel(vk_ulr).add_font("bold")
            all.append(p_bean)
            for i, bean in enumerate(results):
                bean.tracknumber = i + 1
                bean.parent(p_bean)
                all.append(bean)            
                
            self.notetabs.append_tab(vk_ulr, all)
        self.singre_thread.thread_task(inline, vk_ulr)
    
    def search_all_videos(self, query):
        def inline(query):
            results = self.vk.find_video_by_query(query)
            all = []
            p_bean = FModel(query).add_font("bold")
            all.append(p_bean)
            for i, bean in enumerate(results):
                bean.tracknumber = i + 1
                bean.parent(p_bean)
                all.append(bean)
            
            if not results:
                all = self.show_google_results(query)
                
            self.notetabs.append_tab(query, all)
        self.singre_thread.run_with_text(inline, query, "Searching: " + query)
    
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
                
            if not results:
                all = self.show_google_results(query)
            
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
            
            if not results:
                all = self.show_google_results(query)
                
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
                
                if not results:
                    all = self.show_google_results(query)
                    
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
                
                if not results:
                    all = self.show_google_results(query)
                     
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
                if not results:
                    all = self.show_google_results(query)
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
        if bean.path and os.path.isdir(bean.path):
            return self.next()        
        self.play(bean)

    def prev(self):
        bean = self.notetabs.prev()
        if bean.path and os.path.isdir(bean.path):
            return self.prev()
        self.play(bean)

    def filter_tree(self, value):
        self.tree.filter(value)
        self.radio.filter(value)

    def quit(self, *a):
        LOG.info("Controls - Quit")
        self.main_window.hide()
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


    def check_version(self):
        uuid = FC().uuid
        current_version = VERSION        
        try:
            from socket import gethostname
            f = urllib2.urlopen("http://www.foobnix.com/version?uuid=" + uuid + "&host=" + gethostname())
        except:
            return None

        new_version = f.read()
        LOG.info("version", current_version , "|", new_version, "|", uuid)
        f.close()
        if FC().check_new_version and current_version < new_version:
            info_dialog_with_link(_("New version is available"), "foobnix " + new_version, "http://www.foobnix.com/?page=download")            


    def on_load(self):
        for element in self.__dict__:
            if isinstance(self.__dict__[element], LoadSave):
                self.__dict__[element].on_load()
            else:
                LOG.debug("NOT LOAD", self.__dict__[element])
        self.singre_thread = SingreThread(self.search_progress)
        self.main_window.show()
        self.movie_window.hide_all()
        self.check_version()

    def on_save(self):
        for element in self.__dict__:
            if isinstance(self.__dict__[element], LoadSave):
                self.__dict__[element].on_save()
            else:
                LOG.debug("NOT SAVE", self.__dict__[element])
