#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''

import os
import gtk
import copy
import time
import thread
import gobject
import logging
import urllib2

from urllib2 import urlopen
from foobnix.fc.fc import FC
from foobnix.fc.fc_base import FCBase
from foobnix.fc.fc_cache import FCache
from foobnix.regui.model import FModel
from foobnix.regui.state import LoadSave
from foobnix.version import FOOBNIX_VERSION
from foobnix.util.m3u_utils import m3u_reader
from foobnix.util.version import compare_versions
from foobnix.util.text_utils import normalize_text
from foobnix.util.file_utils import get_file_extension
from foobnix.regui.service.vk_service import VKService
from foobnix.util.bean_utils import get_bean_posible_paths
from foobnix.regui.service.music_service import get_all_music_by_paths
from foobnix.regui.service.google_service import google_search_results
from foobnix.regui.treeview.navigation_tree import NavigationTreeControl
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name
from foobnix.util.const import STATE_PLAY, STATE_PAUSE, STATE_STOP, FTYPE_RADIO
from foobnix.helpers.dialog_entry import file_chooser_dialog, \
    directory_chooser_dialog, info_dialog_with_link_and_donate


class BaseFoobnixControls():
    def __init__(self):
        
        self.vk_service = VKService(FC().access_token, FC().user_id)

        self.count_errors = 0
        self.is_scrobbled = False
        self.start_time = None
        
        self.chache_text = None
        
        
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
    
    def love_this_tracks(self, beans=None):        
        if not beans:
            return
        map(self.lastfm_service.love, beans)
    
    def show_google_results(self, query):
        beans = []
        beans.append(FModel('"%s" not found trying Google search' % query))
        g_results = google_search_results(query)
        for line in g_results:
            beans.append(FModel(line).add_is_file(True))
        if not g_results:
            beans.append(FModel('Google not found %s' % query))
            
        return beans
    
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
            
            """play radio, do not check VK"""
            if current.type and current.type == FTYPE_RADIO:
                self.play(current)
                return
            
            if current.path and current.path.startswith("http://"):
                if self.check_path(current):
                    res = self.net_wrapper.execute(self.vk_service.find_one_track, current.get_display_name())
                    if not res:
                        return
                    
                    path = res.path
                    if path:
                        current.path = path
            """play song"""
            self.play(current)
    
    def check_path(self, bean):
        if bean.path:
            if not bean.path.startswith("http://"):
                if os.path.exists(bean.path):
                    return True
            else:
                try:
                    """Timeout not compatible with python 2.5"""
                    #u = urlopen(bean.path, timeout = 7) #@UnusedVariable
                    u = urlopen(bean.path) #@UnusedVariable
                    if not vars().has_key("u"):
                        return False
                    return True
                except:
                    return False
        return False
    
    def save_beans_to(self, beans):
        return None    
   
    def on_chage_player_state(self, state, bean):
        logging.debug("bean state %s" % (state))
        
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
   
    def on_add_folders(self, paths=None):
        if not paths:
            paths = directory_chooser_dialog(_("Choose folders to open"), FC().last_dir)
        if paths:
            def task():
                path = paths[0]
                list = path.split("/")
                FC().last_dir = path[:path.rfind("/")]
                name = list[len(list) - 1]
                parent = FModel(name)
                self.append_to_new_notebook(name, [])
        
                all_beans = []
                all_beans.append(parent)
                for bean in get_all_music_by_paths(paths, self):
                    if not bean.is_file:
                        bean.parent(parent).add_is_file(False)
                    all_beans.append(bean)
        
                if all_beans:
                    self.append_to_current_notebook(all_beans)
                else:
                    self.append([self.SearchCriteriaBeen(_("Nothing found to play in the folder(s)") + paths[0])])
                    
            self.in_thread.run_with_progressbar(task)
    
    def on_add_files(self, paths=None, tab_name=None):
        
        if not paths:       
            paths = file_chooser_dialog(_("Choose file to open"), FC().last_dir)
            copy_paths = copy.deepcopy(paths) 
            for i, path in enumerate(copy_paths):
                if path.lower().endswith(".m3u") or path.lower().endswith(".m3u8"):
                    paths[i:i + 1] = m3u_reader(path)
                    if len(copy_paths) == 1:
                        ext = os.path.splitext(path)[1]
                        tab_name = os.path.basename(path)[:-len(ext)]
                    break
        if paths:
            if paths[0]:
                if isinstance(paths[0], list):
                    path = paths[0][0]
                else:
                    path = paths[0]
            else:
                if isinstance(path, list):
                    path = paths[1][0]
                else:
                    path = paths[1]
               
            if path:
                list_path = path.split("/")
                name = list_path[len(list_path) - 2]
                if not tab_name:
                    tab_name = os.path.split(os.path.dirname(path))[1]
                FC().last_dir = path[:path.rfind("/")]
                self.append_to_new_notebook(tab_name, [])
                parent = FModel(name)
                self.append_to_current_notebook([parent])
            else:
                self.append_to_new_notebook(tab_name, [])
                parent = FModel(tab_name)
                self.append_to_current_notebook([parent])
                              
            beans = []
            for path in paths:
                text = None 
                if isinstance(path, list):
                    text = path[1]
                    path = path[0]
                    bean = FModel(path, path).add_is_file(True)
                else:
                    bean = FModel(path, path).parent(parent).add_is_file(True)
                if text: 
                    bean.text = text
                beans.append(bean)
            if not beans:
                self.append_to_current_notebook([FModel(_("Nothing found to play in the file(s)") + paths[0])])
            else:
                self.append_to_current_notebook(beans)
       
    def set_playlist_tree(self):
        self.notetabs.set_playlist_tree()

    def set_playlist_plain(self):
        self.notetabs.set_playlist_plain()
    
    def load_music_tree(self):
        self.perspective.hide_add_button()
        if not FCache().cache_music_tree_beans[0] and len(FCache().cache_music_tree_beans) == 1:
            
            self.perspective.show_add_button()
            
            self.tree.is_empty = True
            
            if FCache().tab_names[0]:
                self.tabhelper.label.set_label(FCache().tab_names[0] + " ")
        else:
            tabs = len(FCache().cache_music_tree_beans)
            self.tree.simple_append_all(FCache().cache_music_tree_beans[tabs - 1])
            self.tabhelper.label.set_label(FCache().tab_names[tabs - 1] + " ")
            for tab in xrange(tabs - 2, -1, -1):
                
                tree = NavigationTreeControl(self)
                tree.simple_append_all(FCache().cache_music_tree_beans[tab])
                self.tabhelper._append_tab(FCache().tab_names[tab], navig_tree=tree)
                if not FCache().cache_music_tree_beans[tab]: 
                    tree.is_empty = True
                    self.perspective.show_add_button()
            
            logging.info("Tree loaded from cache")
        
        if FC().update_tree_on_start:
            def cycle():
                for n in xrange(len(FCache().music_paths)):
                    tab_child = self.tabhelper.get_nth_page(n)
                    tree = tab_child.get_child()
                    self.update_music_tree(tree, n)
            gobject.idle_add(cycle)
    
    def update_music_tree(self, tree=None, number_of_page=0):
        if not tree:
            tree = self.tree

        logging.info("Update music tree" + str(FCache().music_paths[number_of_page]))
        tree.clear_tree()
        FCache().cache_music_tree_beans[number_of_page] = []
               
        all = []
        
        
        all = get_all_music_by_paths(FCache().music_paths[number_of_page], self)
            
        for bean in all:
            FCache().cache_music_tree_beans[number_of_page].append(bean)
        try:
            self.perspective.hide_add_button()
        except AttributeError:
            logging.warn("Object perspective not exists yet")
        
        if not all:
            tree.is_empty = True
            try:
                self.perspective.show_add_button()
            except AttributeError:
                logging.warn("Object perspective not exists yet")
            all.append(FModel(_("Music not found in folder(s):")))        
            for path in FCache().music_paths[number_of_page]:            
                all.append(FModel(path).add_is_file(True))
        else: tree.is_empty = False
        
        tree.append_all(all)
        tree.ext_width = tree.ext_column.get_width()
          
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
    
    def hide(self):
        self.main_window.hide()
    
    def show_hide(self):
        self.main_window.show_hide()
        
    def show(self):
        self.main_window.show()
    
    def play_pause(self):
        if self.media_engine.get_state() == STATE_PLAY:
            self.media_engine.state_pause()            
        else:
            self.media_engine.state_play()
    
    def seek_up(self):        
        self.media_engine.seek_up()
        
    def seek_down(self):
        self.media_engine.seek_down()
    
    def windows_visibility(self):
        visible = self.main_window.get_property('visible')
        if visible:
            self.main_window.hide()
        else:
            self.main_window.show()

    def state_play(self, remember_position=False, under_pointer_icon=False):
        if self.media_engine.get_state() == STATE_PAUSE and not remember_position:
            self.media_engine.state_play()
            self.statusbar.set_text(self.media_engine.bean.info)
        elif under_pointer_icon:
            tree = self.notetabs.get_current_tree()
            bean = tree.get_bean_under_pointer_icon()
            self.play(bean)
        else:
            self.play_selected_song()
    
    def show_preferences(self):
        self.preferences.show()

    def state_pause(self):
        self.media_engine.state_pause()
    
    def state_stop(self, remember_position=False):
        self.record.hide()
        self.media_engine.state_stop(remember_position)
        if not remember_position:
            self.statusbar.set_text(_("Stopped"))
            self.seek_bar.clear()
        
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
        vk = self.vk_service.find_one_track(bean.get_display_name())
        if vk:
            bean.path = vk.path
            bean.time = vk.time
            return True
        else:
            return False
    
    def play(self, bean):
        if not bean or not bean.is_file:
            return
        if bean.type == FTYPE_RADIO:
            self.record.show()
        else:
            self.record.hide()
        def task():       
            self.seek_bar.clear()
            self.statusbar.set_text(bean.info)
            self.trayicon.set_text(bean.text)
            self.movie_window.set_text(bean.text)        
            self.main_window.set_title(bean.text)
        gobject.idle_add(task)
        thread.start_new_thread(self._play, (bean,))     
        
    def _play(self, bean):
        self.count_errors = 0
        
        if not bean.path:
            bean.path = get_bean_posible_paths(bean)
               
        if not bean.path:            
            if not self.fill_bean_from_vk(bean):
                if self.vk_service.is_show_authorization():
                    return None
                if self.count_errors < 4:
                    time.sleep(0.5)
                    self.count_errors += 1
                    self.next()
           
        if bean.path and os.path.isdir(bean.path):
            return None
        
        self.media_engine.play(bean)  
        self.is_scrobbled = False
        self.start_time = False      
        
        if not get_file_extension(bean.path) in FC().video_formats:
            self.update_info_panel(bean)
            self.set_visible_video_panel(False)
            
    def notify_playing(self, pos_sec, dur_sec, bean, sec):
        self.seek_bar.update_seek_status(pos_sec, dur_sec)
        sec = int(sec) 
        
        if sec > 10 and sec % 11 == 0:
           
            self.net_wrapper.execute(self.lastfm_service.report_now_playing, bean)
                    
        if not self.start_time:
            self.start_time = str(int(time.time()))
        
        if not self.is_scrobbled:            
            
            if sec > dur_sec / 2 or sec > 60:
                
                self.is_scrobbled = True
                self.net_wrapper.execute(self.lastfm_service.report_scrobbled, bean, self.start_time, dur_sec)
                """download music"""
                if FC().automatic_online_save:
                    self.dm.append_task(bean)

            
    def notify_title(self, text):
        logging.debug("Notify title" + text)
        
        self.statusbar.set_text(text)
        text = normalize_text(text)
        self.seek_bar.set_text(text)       
        t_bean = FModel(text).create_from_text(text)                       
        self.update_info_panel(t_bean)
        
        if FC().enable_radio_scrobbler:
            start_time = str(int(time.time()))
            self.net_wrapper.execute(self.lastfm_service.report_now_playing, t_bean)
                    
            if "-" in text and self.chache_text != text:
                text = self.chache_text
                self.net_wrapper.execute(self.lastfm_service.report_scrobbled, t_bean, start_time, 200)
                

    def notify_error(self, msg):
        logging.error("notify error " + msg)
        self.seek_bar.set_text(msg)
        self.info_panel.clear()
        
    def notify_eos(self):
        self.next()

    def player_seek(self, percent):
        self.media_engine.seek(percent)

    def player_volume(self, percent):
        self.media_engine.volume(percent)
    
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
    
    def search_all_videos(self, query):
        def inline():
            results = self.vk_service.find_videos_by_query(query)
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
        self.in_thread.run_with_progressbar(inline)
    
    def search_all_tracks(self, query):
        def inline():
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
        self.in_thread.run_with_progressbar(inline, no_thread=True)

    def search_top_tracks(self, query):
        def inline(query):
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
        self.in_thread.run_with_progressbar(inline, query)


    def search_top_albums(self, query):
        def inline(query):
            results = self.lastfm_service.search_top_albums(query)
            if not results:
                results = []
            self.notetabs.append_tab(query, None)
            albums_already_inserted = []
            for album in results[:15]:
                all = []
                if (album.album.lower() in albums_already_inserted):
                    continue
                album.is_file = False
                tracks = self.lastfm_service.search_album_tracks(album.artist, album.album)
                for i, track in enumerate(tracks):
                    track.tracknumber = i + 1
                    track.parent(album).add_is_file(True)                    
                    all.append(track)
                if (len(all) > 0):
                    all = [album] + all
                    albums_already_inserted.append(album.album.lower())
                    self.notetabs.append_all(all)
                
            if not results:
                all = self.show_google_results(query)
                self.notetabs.append_all(all)
                                   
        self.in_thread.run_with_progressbar(inline, query)

    def search_top_similar(self, query):
        def inline(query):
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
        self.in_thread.run_with_progressbar(inline, query)

    def search_top_tags(self, query):
        def inline(query):
            results = self.lastfm_service.search_top_tags(query)
            if not results:
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
        
        self.in_thread.run_with_progressbar(inline, query)

    def update_info_panel(self, bean):
        self.info_panel.update(bean)

    def append_to_new_notebook(self, text, beans, optimization=False):
        self.notetabs._append_tab(text, beans, None, optimization)

    def append_to_current_notebook(self, beans):
        self.notetabs.append_all(beans)

    def next(self):        
        bean = self.notetabs.next()
        if not bean:
            return
        gap = FC().gap_secs
        time.sleep(gap)
        logging.debug("play current bean is %s" % str(bean.text))
        if bean.path:
            if os.path.isdir(bean.path):
                return None
            if bean.path.startswith("http://"):
                if not self.check_path(bean):
                    path = self.net_wrapper.execute(self.vk_service.find_one_track, bean.get_display_name()).path
                    if path:
                        bean.path = path
                   
        self.play(bean)

    def prev(self):
        bean = self.notetabs.prev()
        if not bean:
            return
        if bean.path:
            if os.path.isdir(bean.path):
                return None
            if bean.path.startswith("http://"):
                if not self.check_path(bean):
                    path = self.net_wrapper.execute(self.vk_service.find_one_track, bean.get_display_name()).path
                    if path:
                        bean.path = path
        
        self.play(bean)

    def filter_by_folder(self, value):
        tree = self.tabhelper.get_current_tree()
        tree.filter_by_folder(value)
        self.radio.filter_by_folder(value)
        self.virtual.filter_by_folder(value)
        
    def filter_by_file(self, value):
        tree = self.tabhelper.get_current_tree()
        tree.filter_by_file(value)
        self.radio.filter_by_file(value)
        self.virtual.filter_by_file(value)
        self.vk_integration.filter_by_folder(query=value, expand=False)

    def quit(self, *a):
        self.state_stop()
        self.main_window.hide()
        self.trayicon.hide()        

        logging.info("Controls - Quit")
        
        self.notetabs.on_quit()
        self.virtual.on_quit()
        self.info_panel.on_quit()
        self.radio.on_quit()
        
        FC().save()
        
        gtk.main_quit()
               
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
            f = urllib2.urlopen("http://www.foobnix.com/version?uuid=" + uuid + "&host=" + gethostname() + "&version=" + current_version + "&platform=" + system)
            #f = urllib2.urlopen("http://localhost:8080/version?uuid=" + uuid + "&host=" + gethostname() + "&v=" + current_version)
        except Exception, e:
            logging.error("Check version error" + str(e))
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
                logging.debug("%f LOAD ON START %s" % (time.time() - init, str(self.__dict__[element])))
        
        """load others"""
        self.movie_window.hide_all()
        
        self.info_panel.hide()
                
        self.change_backgound()
        self.search_progress.stop()
        
        """base layout"""
        self.layout.on_load()
        
        
        """check for new version"""
        
        if os.name == 'nt':
            self.check_version()
        else:
            thread.start_new_thread(self.check_version, ())
        
    def change_backgound(self):
        win = self.main_window
        win.show()
        if FC().background_image:
            img = get_foobnix_resourse_path_by_name(FC().background_image)
            if not img:
                return None
            pixbuf = gtk.gdk.pixbuf_new_from_file(img) #@UndefinedVariable
            pixmap, mask = pixbuf.render_pixmap_and_mask() #@UnusedVariable
            win.set_app_paintable(True)            
            win.window.set_back_pixmap(pixmap, False)        
        else:
            win.set_app_paintable(False)
            win.window.set_back_pixmap(None, False)
        
        
        
    def play_first_file_in_playlist(self):    
        active_playlist_tree = self.notetabs.get_current_tree()
        filter_model = active_playlist_tree.get_model()
        current_model = filter_model.get_model()
                             
        def play_item(iter, active_playlist_tree, filter_model, current_model):
            bean = self.tree.get_bean_from_model_iter(current_model, iter)
            if not bean:
                return
                  
            if bean.is_file:
                self.play(bean)
                tree_selection = active_playlist_tree.get_selection()
                filter_iter = filter_model.convert_child_iter_to_iter(iter)
                tree_selection.select_iter(filter_iter)
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
            
                
