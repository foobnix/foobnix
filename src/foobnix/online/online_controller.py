# -*- coding: utf-8 -*-
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong
'''
Created on Mar 16, 2010

@author: ivan
'''
import os
import gtk

from gobject import GObject #@UnresolvedImport
from foobnix.directory.directory_controller import DirectoryCntr
from foobnix.model.entity import CommonBean
from foobnix.online.information_controller import InformationController
from foobnix.online.online_model import OnlineListModel
from foobnix.online.search_panel import SearchPanel
from foobnix.player.player_controller import PlayerController
from foobnix.util import LOG
from foobnix.util.configuration import FConfiguration
from foobnix.util.mouse_utils import is_double_click, is_rigth_click, \
    is_left_click, is_middle_click
from foobnix.online.google_utils import google_search_resutls
from foobnix.online.dowload_util import  get_file_store_path, \
    save_as_song_thread, save_song_thread

from foobnix.online.song_resource import update_song_path
from foobnix.cue.cue_reader import CueReader
from foobnix.helpers.menu import Popup
from foobnix.util.file_utils import get_file_extenstion
import sys
import urllib

TARGET_TYPE_URI_LIST = 80
dnd_list = [ ('text/uri-list', 0, TARGET_TYPE_URI_LIST) ]

class OnlineListCntr(GObject):
    
    def __init__(self, gxMain, playerCntr):
        self.gx_main = gxMain
        self.directoryCntr = None
        self.playerCntr = playerCntr
        self.current_list_model = None 

        self.search_panel = SearchPanel(gxMain)
        
        self.count = 0
        self.index = 0
        
        self.online_notebook = gxMain.get_widget("online_notebook")
        self.online_notebook.connect('drag-data-received', self.on_drag_data_received)
        self.online_notebook.drag_dest_set(gtk.DEST_DEFAULT_MOTION | 
                 gtk.DEST_DEFAULT_HIGHLIGHT | gtk.DEST_DEFAULT_DROP,
                 dnd_list, gtk.gdk.ACTION_COPY)
        
        add_file_menu = gxMain.get_widget("add-file")
        add_file_menu.connect("activate", self.on_add_file)
        add_folder_menu = gxMain.get_widget("add-folder")
        add_folder_menu.connect("activate", self.on_add_folder)
        
        self.tab_labes = []
        self.default_angel = 90
    
    def get_file_path_from_dnd_dropped_uri(self, uri):
        # get the path to file
        path = ""
        if uri.startswith('file:\\\\\\'): # windows
            path = uri[8:] # 8 is len('file:///')
        elif uri.startswith('file://'): # nautilus, rox
            path = uri[7:] # 7 is len('file://')
        elif uri.startswith('file:'): # xffm
            path = uri[5:] # 5 is len('file:')
        
        path = urllib.url2pathname(path) # escape special chars
        path = path.strip('\r\n\x00') # remove \r\n and NULL
        
        return path
    
    def on_drag_data_received(self, widget, context, x, y, selection, target_type, timestamp):
        TARGET_TYPE_URI_LIST = 80
        dnd_list = [ ('text/uri-list', 0, TARGET_TYPE_URI_LIST) ]
        
        if target_type == TARGET_TYPE_URI_LIST:
            uri = selection.data.strip('\r\n\x00')
            print 'uri', uri
            uri_splitted = uri.split() # we may have more than one file dropped
            paths = []
            for uri in uri_splitted:
                path = self.get_file_path_from_dnd_dropped_uri(uri)
                paths.append(path)
                
            self.on_play_argumens(paths)         
    
    def on_play_argumens(self, args):
        if not args or len(args) <= 1:
            print "no args"
            return None
        dirs = []
        files = []
        for arg in args:
            LOG.info("Arguments", arg)
            if os.path.isdir(arg):
                dirs.append(arg)
            elif os.path.isfile(arg) and get_file_extenstion(arg) in FConfiguration().supportTypes:
                files.append(arg)
        if dirs:
            self.populate_from_dirs(dirs)
        else:
            self.populate_from_files(files)
             
        
    def update_label_angel(self, angle):
        for label in self.tab_labes:
            label.set_angle(angle)
    
    def set_tab_left(self):
        LOG.info("Set tabs Left")
        self.online_notebook.set_tab_pos(gtk.POS_LEFT)
        self.update_label_angel(90)
        self.default_angel = 90
        self.online_notebook.set_show_tabs(True)
        FConfiguration().tab_position = "left"
    
    def set_tab_top(self):
        LOG.info("Set tabs top")
        self.online_notebook.set_tab_pos(gtk.POS_TOP)
        self.update_label_angel(0)
        self.default_angel = 0
        self.online_notebook.set_show_tabs(True)
        FConfiguration().tab_position = "top"
    
    def set_tab_no(self):
        LOG.info("Set tabs no")
        self.online_notebook.set_show_tabs(False)
        FConfiguration().tab_position = "no"
   
    
    def on_add_file(self, *a):
        chooser = gtk.FileChooserDialog(title=_("Choose file to open"), action=gtk.FILE_CHOOSER_ACTION_OPEN, buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_select_multiple(True)
        if FConfiguration().last_dir:
                chooser.set_current_folder(FConfiguration().last_dir)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            paths = chooser.get_filenames()
            self.populate_from_files(paths)
            
        elif response == gtk.RESPONSE_CANCEL:
            LOG.info('Closed, no files selected')
        chooser.destroy()
        print "add file"  
    
    def populate_from_files(self, paths):
        if not paths:
            return None
        path = paths[0]
        list = paths[0].split("/")
        
        FConfiguration().last_dir = path[:path.rfind("/")]
        self.append_notebook_page(list[len(list) - 2])
        beans = []
        for path in paths:
            bean = self.directoryCntr.get_common_bean_by_file(path)
            beans.append(bean)
        if beans:            
            self.append_and_play(beans)
        else:
            self.append([self.SearchCriteriaBeen(_("Nothing found to play in the file(s)") + paths[0])])
    
    def populate_from_dirs(self, paths):
        if not paths :
            return None
        
        path = paths[0]
        
        list = path.split("/")
        FConfiguration().last_dir = path[:path.rfind("/")]
        self.append_notebook_page(list[len(list) - 1])
        
        all_beans = []
        for path in paths:
            if path == "/":
                LOG.info("Skip root folder")
                continue;            
            beans = self.directoryCntr.get_common_beans_by_folder(path)
            for bean in beans:
                all_beans.append(bean)
            
        if all_beans:            
            self.append_and_play(all_beans)
        else:
            self.append([self.SearchCriteriaBeen(_("Nothing found to play in the folder(s)") + paths[0])])

    def on_add_folder(self, *a):
        chooser = gtk.FileChooserDialog(title=_("Choose directory with music"), action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_select_multiple(True)
        if FConfiguration().last_dir:
                chooser.set_current_folder(FConfiguration().last_dir)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            paths = chooser.get_filenames()
            self.populate_from_dirs(paths)
            
        elif response == gtk.RESPONSE_CANCEL:
            LOG.info('Closed, no files selected')
        chooser.destroy()
        print "add folder"
    
    def register_directory_cntr(self, directoryCntr):
        self.directoryCntr = directoryCntr
        self.info = InformationController(self.gx_main, self.playerCntr, directoryCntr, self.search_panel, self)
    
    def none(self, *a):
        return False
    
    def create_notebook_tab(self):
        treeview = gtk.TreeView()
        treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        treeview.set_rubber_banding(True)
        
        treeview.set_reorderable(True)
        model = OnlineListModel(treeview)
        self.current_list_model = model
        
        treeview.connect("drag-end", self.on_drag_end)
        treeview.connect("button-press-event", self.onPlaySong, model)
        
        treeview.show()
        
        window = gtk.ScrolledWindow()
        window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        window.add_with_viewport(treeview)
        window.show()
        return  window    
        
    def append_notebook_page(self, name):
        LOG.info("append new tab")
        if name and len(name) > 50:
            name = name[:50]
                        
        label = gtk.Label(name)
        
        label.set_angle(self.default_angel)
        label.show()
        
        self.tab_labes.append(label)
        
        event_box = gtk.EventBox()
        event_box.add(label)
        event_box.connect('event', self.on_tab_click)
         
              
                        
        self.online_notebook.prepend_page(self.create_notebook_tab(), event_box)
        self.online_notebook.set_current_page(0)
        
        if self.online_notebook.get_n_pages() > FConfiguration().count_of_tabs:
            self.online_notebook.remove_page(self.online_notebook.get_n_pages() - 1)
        
    
    def on_tab_click(self, w, e):
        """ double left or whell pressed"""
        
        if is_middle_click(e):
            LOG.info("Close Current TAB")
            self.delete_tab()
        if is_rigth_click(e):
            menu = Popup()            
            menu.add_item(_("Close"), gtk.STOCK_DELETE, self.delete_tab, None)
            menu.show(e)
    
    def delete_tab(self):
        page = self.online_notebook.get_current_page()            
        self.online_notebook.remove_page(page)
        

    def add_selected_to_playlist(self):
        selected = self.current_list_model.get_selected_bean()
        LOG.info("SELECTED", selected)
        self.directoryCntr.set_active_view(DirectoryCntr.VIEW_VIRTUAL_LISTS)
        if selected.type == CommonBean.TYPE_MUSIC_URL:
            selected.parent = None
            self.directoryCntr.append_virtual([selected])
        elif selected.type in [CommonBean.TYPE_FOLDER, CommonBean.TYPE_GOOGLE_HELP, CommonBean.TYPE_RADIO_URL]:
            selected.type = CommonBean.TYPE_FOLDER
            results = []
            for i in xrange(self.current_list_model.get_size()):
                searchBean = self.current_list_model.getBeenByPosition(i)
            #LOG.info("Search", searchBean
                if str(searchBean.name) == str(selected.name):
                    searchBean.parent = None
                    results.append(searchBean)
                elif str(searchBean.parent) == str(selected.name):
                    results.append(searchBean)
                else:
                    LOG.info(str(searchBean.parent) + " != " + str(selected.name))
            
            self.directoryCntr.append_virtual(results)
        LOG.info("drug")

    def on_drag_end(self, *ars):
        self.add_selected_to_playlist()

    def show_searching(self, sender, query):
        self.append_notebook_page(query)
        self.append([self.SearchingCriteriaBean(query)])
        pass
    
    def show_results(self, sender, query, beans, criteria=True):
        #time.sleep(0.1)
        #self.online_notebook.remove_page(0)
        #self.append([self.SearchingCriteriaBean(query)])
        self.append_notebook_page(query)                
        #self.append_notebook_page(query)
        #time.sleep(0.1)
        #self.current_list_model.clear()
        
        LOG.debug("Showing search results")
        if beans:
            if criteria:
                self.append([self.SearchCriteriaBeen(query)])
            self.append(beans)
        else:
            LOG.debug("Nothing found get try google suggests")
            self.google_suggests(query)


    def google_suggests(self, query):
        self.append([self.TextBeen(query + _(" not found on last.fm, wait for google suggests ..."))])
        suggests = google_search_resutls(query, 15)
        if suggests:
            for line in suggests:            
                self.append([self.TextBeen(line, color="YELLOW", type=CommonBean.TYPE_GOOGLE_HELP)])
        else :
            self.append([self.TextBeen(_("Google not found suggests"))])

    def TextBeen(self, query, color="RED", type=CommonBean.TYPE_FOLDER):
        return CommonBean(name=query, path=None, color=color, type=type)

    def SearchCriteriaBeen(self, name):
        return CommonBean(name=name, path=None, color="#4DCC33", type=CommonBean.TYPE_FOLDER)

    def SearchingCriteriaBean(self, name):
        return CommonBean(name=_("Searching: ") + name + _(" ... please wait a second"), path=None, color="GREEN", type=CommonBean.TYPE_FOLDER)


    
    def _populate_model(self, beans):
        normilized = []
        """first add cue files"""
        for bean in beans:
            LOG.info("append", bean, bean.path)
            if bean.path and bean.path.lower().endswith(".cue"):
                cues = CueReader(bean.path).get_common_beans()
                for cue in cues:                
                    self.current_list_model.append(cue)
                    normilized.append(cue)
        
        """end big file to the end"""
        for bean in beans:
            id3 = bean.getMp3TagsName()            
            if id3:
                bean.id3, bean.name = bean.name, id3
                
            if not bean.path or (bean.path and not bean.path.lower().endswith(".cue")):
                self.current_list_model.append(bean)
                
                normilized.append(bean)
        return normilized

    def append(self, beans):
        self._populate_model(beans)
        self.current_list_model.repopulate(-1)

    def append_and_play(self, beans):
        beans = self._populate_model(beans)
        if not beans:
            return None
        self.index = 0    
        self.current_list_model.repopulate(self.index)
        song = beans[self.index]
        LOG.info("PLAY", song)
        self.playerCntr.playSong(song)
    
        
        
    def on_play_selected(self, similar_songs_model):
        playlistBean = similar_songs_model.get_selected_bean()
        if not playlistBean:
            return None
        LOG.info("play", playlistBean)
        LOG.info("type", playlistBean.type)
        if playlistBean.type == CommonBean.TYPE_MUSIC_URL:
            self.playBean(playlistBean)
        elif playlistBean.type == CommonBean.TYPE_GOOGLE_HELP:
            self.search_panel.set_text(playlistBean.name)
        else:
            self.playBean(playlistBean)
    
    def show_save_as_dialog(self, songs):
        LOG.debug("Show Save As Song dialog", songs)    
        chooser = gtk.FileChooserDialog(title=_("Choose directory to save song"), action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            path = chooser.get_filename()
            save_as_song_thread(songs, path)
        elif response == gtk.RESPONSE_CANCEL:
            LOG.info('Closed, no files selected')
        chooser.destroy()
        
    def show_info(self, songs):
        if not songs:
            return None
    
        result = ""
        for song in songs:
            result += song.getArtist() + " - " + song.getTitle() + "\n"
        md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                               gtk.BUTTONS_CLOSE, result)
        md.run()
        md.destroy()

    def changed(self, a, type=None):
        if self.paths:
            a.select_range(self.paths[0], self.paths[len(self.paths) - 1])

    def onPlaySong(self, w, e, similar_songs_model): 
        
        self.current_list_model = similar_songs_model
        songs = similar_songs_model.get_all_selected_beans()    
        self.index = similar_songs_model.get_selected_index()
        
        #selected rows
        treeselection = similar_songs_model.widget.get_selection()
        model, self.paths = treeselection.get_selected_rows()
        
        #LOG.debug("Seletected index", self.index, songs)
        if is_left_click(e):
            self.paths = None
            LOG.debug("SAVE SELECTED", self.paths)
        elif is_double_click(e):
            self.paths = None
            self.on_play_selected(similar_songs_model);
        elif is_rigth_click(e):
            treeselection.connect('changed', self.changed, True)
            
            menu = Popup()
            menu.add_item(_("Play"), gtk.STOCK_MEDIA_PLAY, self.on_play_selected, similar_songs_model)
            menu.add_item(_("Save"), gtk.STOCK_SAVE, save_song_thread, songs)
            menu.add_item(_("Save as"), gtk.STOCK_SAVE_AS, self.show_save_as_dialog, songs)
            menu.add_item(_("Add to virtual"), gtk.STOCK_ADD, self.add_selected_to_playlist)
            menu.add_item(_("Delete from list"), gtk.STOCK_REMOVE, similar_songs_model.remove_selected)
            menu.add_item(_("Show info"), gtk.STOCK_INFO, self.show_info, songs)
            menu.show(e)
            
            
            treeselection.select_all()

    def playBean(self, playlistBean):
        if playlistBean.type in [CommonBean.TYPE_MUSIC_URL, CommonBean.TYPE_MUSIC_FILE]:
            self.setSongResource(playlistBean)

            LOG.info("Song source path", playlistBean.path)

            if not playlistBean.path:
                self.count += 1
                LOG.info(self.count)
                playlistBean.setIconErorr()
                if self.count < 5   :
                    return self.playBean(self.getNextSong())
                return

        self.playerCntr.set_mode(PlayerController.MODE_ONLINE_LIST)
        self.playerCntr.playSong(playlistBean)
                 
        self.current_list_model.repopulate(self.index)


    def setSongResource(self, playlistBean, update_song_info=True):
        if not playlistBean.path:
            if playlistBean.type == CommonBean.TYPE_MUSIC_URL:

                file = get_file_store_path(playlistBean)
                if os.path.isfile(file) and os.path.getsize(file) > 1:
                    LOG.info("Find file dowloaded")
                    playlistBean.path = file
                    playlistBean.type = CommonBean.TYPE_MUSIC_FILE
                    return True
                else:
                    LOG.info("FILE NOT FOUND IN SYSTEM")

                #Seach by vk engine
                update_song_path(playlistBean)

            #if update_song_info:
            """retrive images and other info"""
            #self.info.show_song_info(playlistBean)

    def nextBean(self):
        if not self.current_list_model:
            return None
        if FConfiguration().isRandom:            
            return self.current_list_model.get_random_bean()   
        
        self.index += 1
        
        if self.index >= self.current_list_model.get_size():
                self.index = 0
                if not FConfiguration().isRepeat:
                    self.index = self.current_list_model.get_size()
                    return None
            
        return self.current_list_model.getBeenByPosition(self.index)
            
    def prevBean(self):
        if not self.current_list_model:
            return None

        if FConfiguration().isRandom:            
            return self.current_list_model.get_random_bean()
        
        self.index -= 1        
        list = self.current_list_model.get_all_beans()
        
        if self.index <= 0:
            self.index = self.current_list_model.get_size()

        playlistBean = self.current_list_model.getBeenByPosition(self.index)
        return playlistBean

#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

    def getNextSong(self):

        currentSong = self.nextBean()

        if(currentSong.type == CommonBean.TYPE_FOLDER):
            currentSong = self.nextBean()

        self.setSongResource(currentSong)
        LOG.info("PATH", currentSong.path)
        
        self.current_list_model.repopulate(currentSong.index);
        return currentSong
    
    
    def setState(self, state):
        #TODO
        pass
        
    def getState(self):
        #TODO
        pass
    
    def getPrevSong(self):
        playlistBean = self.prevBean()

        if(playlistBean.type == CommonBean.TYPE_FOLDER):
            self.getPrevSong()

        self.setSongResource(playlistBean)

        self.current_list_model.repopulate(playlistBean.index);
        return playlistBean
 
