# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2010

@author: ivan
'''
import os

from foobnix.util import LOG



from foobnix.directory.directory_model import DirectoryModel
from foobnix.model.entity import CommonBean
from foobnix.util.configuration import FConfiguration
from foobnix.util.file_utils import isDirectory, get_file_extenstion
import gtk
from foobnix.directory.pref_list_model import PrefListModel
import gettext
from foobnix.util.mouse_utils import  is_double_left_click, is_rigth_click
from mutagen.mp3 import MP3
from foobnix.util.time_utils import normilize_time
from foobnix.radio.radios import  RadioFolder
from foobnix.cue.cue_reader import CueReader
import thread
import time
from foobnix.helpers.menu import Popup


gettext.install("foobnix", unicode=True)

class DirectoryCntr():

    VIEW_LOCAL_MUSIC = 0
    VIEW_RADIO_STATION = 1
    VIEW_VIRTUAL_LISTS = 2
    VIEW_CHARTS_LISTS = 2

    DEFAULT_LIST = "Default list";
    #DEFAULT_LIST_NAME = _("Default list");


    def __init__(self, gxMain, playlistCntr, virtualListCntr):

        self.playlistCntr = playlistCntr
        self.virtualListCntr = virtualListCntr



        widget = gxMain.get_widget("direcotry_treeview")
        self.current_list_model = DirectoryModel(widget)
        widget.connect("button-press-event", self.onMouseClick)
        widget.connect("key-release-event", self.onTreeViewDeleteItem)

        widget.connect("drag-end", self.on_drag_get)

        "Pref lists "
        self.prefListMap = {self.DEFAULT_LIST : []}
        self.currentListMap = self.DEFAULT_LIST


        prefList = gxMain.get_widget("treeview3")
        prefList.connect("button-press-event", self.onPreflListMouseClick)
        prefList.connect("key-release-event", self.onPreflListDeleteItem)
        prefList.connect("cursor-changed", self.onPreflListSelect)
        self.prefModel = PrefListModel(prefList, self.prefListMap)


        self.filter = gxMain.get_widget("filter-entry")
        self.filter.connect("key-release-event", self.onFiltering)

        show_local = gxMain.get_widget("show_local_music_button")
        show_local.connect("toggled", self.onChangeView, self.VIEW_LOCAL_MUSIC)
        show_local.connect("button-press-event", self.on_local_toggle_click)
        show_local.view_type = self.VIEW_LOCAL_MUSIC
        self.active_view = self.VIEW_LOCAL_MUSIC

        show_radio = gxMain.get_widget("show_radio_button")
        show_radio.connect("toggled", self.onChangeView, self.VIEW_RADIO_STATION)
        show_radio.view_type = self.VIEW_RADIO_STATION

        show_play_list = gxMain.get_widget("show_lists_button")
        show_play_list.connect("toggled", self.onChangeView, self.VIEW_VIRTUAL_LISTS)
        show_play_list.view_type = self.VIEW_VIRTUAL_LISTS

        self.search_mode_buttons = []
        self.search_mode_buttons.append(show_local)
        self.search_mode_buttons.append(show_radio)
        self.search_mode_buttons.append(show_play_list)


        #show_charts_ = gxMain.get_widget("show_charts_button")
        #show_charts_.connect("clicked", self.onChangeView, self.VIEW_CHARTS_LISTS)

        self.onChangeView


        self.saved_model = None

        self.radio_folder = RadioFolder()


        self.cache_music_beans = FConfiguration().cache_music_beans
        self.radio_update_thread = None

        self.direcotory_thread = None
        self.addAll(reload=False)
        self.direcotory_thread = None


    def getState(self):
        return self.prefListMap

    def setState(self, preflists):
        self.prefListMap = preflists
        self.prefModel.prefListMap = preflists
        for key in self.prefListMap:
            LOG.info("add key to virtual list", unicode(key))
            self.prefModel.append(key)



    def getPrefListBeans(self, preflist=DEFAULT_LIST):


        if preflist in self.prefListMap:
            return self.prefListMap[preflist]
        return None

    def appendToPrefListBeans(self, beans, preflist=DEFAULT_LIST):
        if not preflist in self.prefListMap:
            LOG.info("Key not found")
            self.prefListMap[preflist] = []

        if beans:
            for bean in beans:
                self.prefListMap[preflist].append(bean)

    def clearPrefList(self, listName):
        if listName in self.prefListMap:
            self.prefListMap[listName] = []


    def onPreflListSelect(self, *args):
        #self.view_list.set_active(self.VIEW_VIRTUAL_LISTS)
        self.currentListMap = self.prefModel.getSelected()

        if self.currentListMap in self.prefListMap:
            beans = self.prefListMap[self.currentListMap]
            self.display_virtual(beans)
        else:
            self.clear()


    def onPreflListMouseClick(self, w, event):
        if event.button == 3 and event.type == gtk.gdk._2BUTTON_PRESS: #@UndefinedVariable
            LOG.debug("Create new paly list")
            unknownListName = _("New play list")
            if not self.prefModel.isContain(unknownListName):
                self.prefModel.append(unknownListName)
                self.prefListMap[unknownListName] = []

    def onPreflListDeleteItem(self, w, event):

        if event.type == gtk.gdk.KEY_RELEASE: #@UndefinedVariable
            #Enter pressed
            LOG.info(event.keyval)
            LOG.info(event.hardware_keycode)
            if event.hardware_keycode == 119 or event.hardware_keycode == 107:
                if self.prefModel.getSelectedIndex() > 0:
                    del self.prefListMap[unicode(self.prefModel.getSelected())]
                    self.prefModel.removeSelected()

                    self.clear()


    def all(self, *args):
        for arg in args:
            LOG.info(arg)


    def getModel(self):
        return self.current_list_model

    def on_drag_get(self, *args):
        self.populate_playlist(append=True)

    "TODO: set active button state"
    def set_active_view(self, view_type):
        for button in self.search_mode_buttons:
            if button.view_type == view_type:
                button.set_active(True)
            else:
                button.set_active(False)

    def on_local_toggle_click(self, w, event):
        if is_rigth_click(event):
            menu = Popup()
            menu.add_item(_("Update Music Tree"), gtk.STOCK_REFRESH, self.addAll, True)
            menu.show(event)

    def onChangeView(self, clicked_button, active_view):
        if all([not button.get_active() for button in self.search_mode_buttons]):
            clicked_button.set_active(True)

        # if the button should become unchecked, then do nothing
        if not clicked_button.get_active():
            return

        # so, the button becomes checked. Uncheck all other buttons
        for button in self.search_mode_buttons:
            if button != clicked_button:
                button.set_active(False)



        self.active_view = active_view

        if active_view == self.VIEW_LOCAL_MUSIC:
            self.clear()
            self.addAll(reload=False)


        elif active_view == self.VIEW_RADIO_STATION:
            if not self.radio_update_thread:
                #self.radio_update_thread = thread.start_new_thread(self.update_radio_thread, ())
                self.update_radio_thread()


        elif active_view == self.VIEW_VIRTUAL_LISTS:
            items = self.getPrefListBeans(self.DEFAULT_LIST)
            self.display_virtual(items)


    def update_radio_thread(self):
        self.clear()
        files = self.radio_folder.get_radio_FPLs()
        for fpl in files:
            parent = self.current_list_model.append(None, CommonBean(name=fpl.name, path=None,
                                                                     font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER))
            for radio, urls in fpl.urls_dict.iteritems():
                self.current_list_model.append(parent, CommonBean(name=radio, path=urls[0],
                                                                  font="normal", is_visible=True, type=CommonBean.TYPE_RADIO_URL,
                                                                  parent=fpl.name))
        self.radio_update_thread = None

    def append_virtual(self, beans=None):
        LOG.debug("Current virtual list", self.currentListMap)
        if not self.currentListMap:
            self.currentListMap = self.DEFAULT_LIST

        self.appendToPrefListBeans(beans, self.currentListMap)
        items = self.getPrefListBeans(self.currentListMap)
        self.display_virtual(items)

    def display_virtual(self, items):
        self.clear()

        "Displya list title"
        self.current_list_model.append(None, CommonBean(name="[" + self.currentListMap + "]", path=None,
                                                        font="bold", is_visible=True, type=CommonBean.TYPE_LABEL,
                                                        parent=None, index=0))

        if not items:
            return None


        parent = None

        i = 1
        for item in items:
            LOG.info(item)
            if item.parent == None:
                parent = self.current_list_model.append(None, CommonBean(name=item.name, path=item.path,
                                                                         font="normal", is_visible=True, type=item.type,
                                                                         parent=item.parent, index=i))
            else:
                self.current_list_model.append(parent, CommonBean(name=item.name, path=item.path,
                                                                  font="normal", is_visible=True, type=item.type,
                                                                  parent=item.parent, index=i))
            i += 1



    def onTreeViewDeleteItem(self, w, event):
        if self.active_view != self.VIEW_VIRTUAL_LISTS:
            return

        LOG.info(event)
        if event.type == gtk.gdk.KEY_RELEASE: #@UndefinedVariable
            #Enter pressed
            LOG.info(event.keyval)
            LOG.info(event.hardware_keycode)
            if event.hardware_keycode == 119 or event.hardware_keycode == 107:
                LOG.info("Delete")
                bean = self.current_list_model.get_selected_bean()
                LOG.info(bean.index)
                if bean.index > 0:
                    self.virtualListCntr.items = self.prefListMap[self.currentListMap]
                    self.virtualListCntr.remove_with_childrens(bean.index - 1, bean.parent)
                    self.append_virtual()


    def onFiltering(self, *args):
        text = self.filter.get_text()
        LOG.info("filtering by text", text)
        self.current_list_model.filterByName(text)


    def onMouseClick(self, w, event):
        if is_double_left_click(event):
            self.populate_playlist()
        if is_rigth_click(event):
            menu = Popup()
            menu.add_item(_("Update Music Tree"), gtk.STOCK_REFRESH, self.addAll, True)
            menu.add_item(_("Play"), gtk.STOCK_MEDIA_PLAY, self.populate_playlist, None)
            menu.add_item(_("Add folder"), gtk.STOCK_OPEN, self.add_folder, None)
            menu.show(event)

    def add_folder(self):
        chooser = gtk.FileChooserDialog(title=_("Choose directory with music"),
                                        action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_select_multiple(True)
        if FConfiguration().last_dir:
                chooser.set_current_folder(FConfiguration().last_dir)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            paths = chooser.get_filenames()
            path = paths[0]
            FConfiguration().last_dir = path[:path.rfind("/")]
            for path in paths:
                if path in FConfiguration().media_library_path:
                    pass
                else:
                    FConfiguration().media_library_path.append(path)

            self.addAll(True)

        elif response == gtk.RESPONSE_CANCEL:
            LOG.info('Closed, no files selected')
        chooser.destroy()
        print "add folder(s)"


    def update_songs_time(self, songs):
        for song in songs:
            if song.path and song.path.endswith("3") and not song.time:
                try:
                    audio = MP3(song.path)
                    song.time = normilize_time(audio.info.length)
                except:
                    pass

                #audio = EasyID3(song.path)
                #song.title = str(audio["title"][0])
                #song.artist =str( audio["artist"][0])
                #song.album = str(audio["album"][0])
                #song.tracknumber= str(audio["tracknumber"][0])
                #LOG.info(song.title, song.artist, song.album




    def populate_playlist(self, append=False):
        LOG.info("Drug begin")
        directoryBean = self.current_list_model.get_selected_bean()
        if not directoryBean:
            return

        LOG.info("Select: ", directoryBean.name, directoryBean.type)
        LOG.info("Drug type", directoryBean.type)

        if append and not self.playlistCntr.current_list_model:
                self.playlistCntr.append_notebook_page(directoryBean.name)

        if directoryBean.type in [CommonBean.TYPE_FOLDER, CommonBean.TYPE_GOOGLE_HELP] :
            songs = self.current_list_model.getChildSongBySelected()

            self.update_songs_time(songs)
            LOG.info("Select songs", songs)
            if not songs:
                return

            if append:
                self.playlistCntr.append(songs)
            else:
                self.playlistCntr.append_notebook_page(directoryBean.name)
                self.playlistCntr.append_and_play(songs)

        elif directoryBean.type == CommonBean.TYPE_LABEL:
            songs = self.current_list_model.getAllSongs()

            if append:
                self.playlistCntr.append(songs)
            else:
                self.playlistCntr.append_notebook_page(directoryBean.name)
                self.playlistCntr.append_and_play(songs)
        else:
            if append:
                self.playlistCntr.append([directoryBean])
            else:
                self.playlistCntr.append_notebook_page(directoryBean.name)
                self.playlistCntr.append_and_play([directoryBean])



    def getALLChildren(self, row, string):
        for child in row.iterchildren():
            name = child[self.POS_NAME].lower()
            if name.find(string) >= 0:
                LOG.info("FIND SUB :", name, string)
                child[self.POS_VISIBLE] = True
            else:
                child[self.POS_VISIBLE] = False



    def updateDirectoryByPath(self, path=None):
        self.current_list_model.clear()
        self.addAll(reload=True)

    def clear(self):
        self.current_list_model.clear()

    def getAllSongsByPath(self, path):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = sorted(list)
        result = []
        for file_name in list:
            if get_file_extenstion(file_name) not in FConfiguration().supportTypes:
                    continue

            full_path = path + "/" + file_name

            if not isDirectory(full_path):
                bean = CommonBean(name=file_name, path=full_path, type=CommonBean.TYPE_MUSIC_FILE)
                result.append(bean)

        LOG.debug(result)
        return result

    cachModel = []

    def addAllThread(self, reload):
        if reload:
            self.cache_music_beans = []

        if not self.cache_music_beans:
            self.clear()
            self.current_list_model.append(None, CommonBean(name=_("Updating music, please wait... ") , path=None,
                                                            font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER,
                                                            parent=None))
            for path in FConfiguration().media_library_path:
                if path == "/":
                    FConfiguration().media_library_path = None
                    LOG.error("not possible value in the path!!!")
                    self.current_list_model.append(None, CommonBean(name=_("Music not found") + path, path=None,
                                                                    font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER,
                                                                    parent=None))
                    break;

                LOG.info("Media path is", path)
                self.go_recursive(path, None)
            FConfiguration().cache_music_beans = self.cache_music_beans

        if not self.cache_music_beans:
            self.current_list_model.clear()
            self.current_list_model.append(None, CommonBean(name=_("Music not found"), path=None,
                                                            font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER,
                                                            parent=None))
            for path in FConfiguration().media_library_path:
                self.current_list_model.append(None, CommonBean(name=path, path=None,
                                                                font="normal", is_visible=True, type=CommonBean.TYPE_FOLDER,
                                                                parent=None))

        else:
            self.show_music_tree(self.cache_music_beans)

        self.direcotory_thread = None


    """show music tree by parent-child relations"""
    def show_music_tree(self, beans):
        self.current_list_model.clear()
        hash = {None:None}
        for bean in beans:
            if hash.has_key(bean.parent):
                iter = hash[bean.parent]
            else:
                iter = None

            new_iter = self.current_list_model.append(iter, bean)
            hash[bean.path] = new_iter



    def addAll(self, reload=False):

        self.addAllThread(reload)


        if not self.direcotory_thread:
            pass
           # self.direcotory_thread = thread.start_new_thread(self.addAllThread, (reload,))
            #self.addAllThread(reload)
        else:
            LOG.info("Directory is updating...")

        #self.addAllThread()

    def sortedDirsAndFiles(self, path, list):
        files = []
        directories = []
        #First add dirs
        for file in list:
            full_path = path + "/" + file
            if isDirectory(full_path):
                directories.append(file)
            else:
                files.append(file)

        return sorted(directories) + sorted(files)

    def isDirectoryWithMusic(self, path):
        LOG.info("Begin read", path)
        if isDirectory(path):
            dir = os.path.abspath(path)
            list = None
            try:
                list = os.listdir(dir)
            except OSError, e:
                LOG.info("Can'r get list of dir", e)

            if not list:
                return False

            for file in list:
                full_path = path + "/" + file
                if isDirectory(full_path):
                    if self.isDirectoryWithMusic(full_path):
                        return True
                else:
                    if get_file_extenstion(file) in FConfiguration().supportTypes:
                        return True

        return False


    def get_common_beans_by_folder(self, path):
        LOG.info("begin schanning")
        self.result = []
        self.scanner(path, None)
        return self.result

    def get_common_bean_by_file(self, full_path):
        if not os.path.isfile(full_path):
            LOG.warn(full_path + " not a file")
            return None
        ext = get_file_extenstion(full_path)
        LOG.info("Extension is ", ext)
        if ext not in FConfiguration().supportTypes:
            LOG.warn(full_path + " extensions not supported")
            return None

        """check cue is valid"""
        if full_path.endswith(".cue") and not CueReader(full_path).is_cue_valid():
            LOG.warn(full_path + " cue not valid")
            return None

        return CommonBean(name=full_path, path=full_path,
                          font="normal", is_visible=True, type=CommonBean.TYPE_MUSIC_FILE,
                          parent=full_path)


    def scanner(self, path, level):
        LOG.info("scanner", path)
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = self.sortedDirsAndFiles(path, list)

        for file in list:

            full_path = path + "/" + file

            if not isDirectory(full_path) and get_file_extenstion(file) not in FConfiguration().supportTypes:
                continue

            """check cue is valid"""
            if full_path.endswith(".cue") and not CueReader(full_path).is_cue_valid():
                continue

            if self.isDirectoryWithMusic(full_path):
                #self.result.append(CommonBean(name=file, path=full_path,
                #                              font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER,
                #                              parent=level))
                self.scanner(full_path, None)
            else:
                if not isDirectory(full_path):
                    self.result.append(CommonBean(name=file, path=full_path,
                                       font="normal", is_visible=True, type=CommonBean.TYPE_MUSIC_FILE,
                                       parent=level))


    def go_recursive(self, path, level):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = self.sortedDirsAndFiles(path, list)

        for file in list:

            full_path = path + "/" + file

            if not isDirectory(full_path) and get_file_extenstion(file) not in FConfiguration().supportTypes:
                continue

            """check cue is valid"""
            if full_path.endswith(".cue") and not CueReader(full_path).is_cue_valid():
                continue

            if self.isDirectoryWithMusic(full_path):
                #LOG.debug("directory", file)
                self.cache_music_beans.append(CommonBean(name=file, path=full_path,
                                                         font="bold", is_visible=True, type=CommonBean.TYPE_FOLDER,
                                                         parent=level))
                self.go_recursive(full_path, full_path)
            else:
                if not isDirectory(full_path):
                    self.cache_music_beans.append(CommonBean(name=file, path=full_path,
                                                             font="normal", is_visible=True, type=CommonBean.TYPE_MUSIC_FILE,
                                                             parent=level))
                    #LOG.debug("file", file)
