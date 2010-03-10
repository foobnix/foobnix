#!/usr/bin/env python
import gtk.glade
import gst


import os
import time
from foobnix.confguration import FConfiguration
from foobnix.player_engine import PlayerEngine
from foobnix.playlist import PlayList
from foobnix.dirlist import DirectoryList
from foobnix.song import Song
from foobnix.plsparser import PLSParser
from foobnix.file_utils import getSongFromWidget
from foobnix.util import LOG
from foobnix.mouse_utils import is_double_click
from foobnix.gui.InitGlade import InitGlade
from foobnix.gui.TrayIcon import TrayIcon
from foobnix.service.WindowService import WindowService
from foobnix.gui.MainWindowWidget import MainWindowWidget
from foobnix.bus.BusController import BusController


class FoobNIX:
        def __init__(self): 
     
            initGlade = InitGlade()
            
            busController = BusController()
                        
            self.mainWindowGlade = MainWindowWidget(busController).getGlade()
            self.popUpGlade = initGlade.getTopLevel("popUpWindow")
            aboutGlade = initGlade.getTopLevel("aboutdialog")
            
            
            
            
            signalsPopUp = {
                    "on_close_clicked" :self.quitApp,
                    "on_play_clicked" :self.onPlayButton,
                    "on_pause_clicked" :self.onPauseButton,
                    "on_next_clicked" :self.onPlayNextButton,
                    "on_prev_clicked" :self.onPlayPrevButton,
                    "on_cancel_clicked": self.closePopUP
            }
            
                        
            self.aboutDialog = aboutGlade.get_widget("aboutdialog")
            
            
            self.popUpGlade.signal_autoconnect(signalsPopUp)
            
            #self.icon = gtk.StatusIcon()
            #self.icon.set_tooltip("Foobnix music playerEngine")
            #self.icon.set_from_stock("gtk-media-play")
            #self.icon.connect("activate", self.iconLeftClick)
            
            
            #self.icon.connect("popup-menu", self.iconRightClick)
            #self.icon.connect("scroll-event", self.scrollChanged)
            
            self.isShowMainWindow = True
                            
            
            self.timeLabelWidget = self.mainWindowGlade.get_widget("seek_progressbar")
            self.window = self.mainWindowGlade.get_widget("foobnixWindow")
           
           
            windowService = WindowService(self.window)
            self.icon = TrayIcon(windowService)
           
            self.window.maximize()
                
            self.menuPopUp = self.popUpGlade.get_widget("popUpWindow")
            
            self.volumeWidget = self.mainWindowGlade.get_widget("volume_hscale")
            
            
            self.seekWidget = self.mainWindowGlade.get_widget("seek_progressbar")
            
            self.directoryListWidget = self.mainWindowGlade.get_widget("direcotry_treeview")
            self.playListWidget = self.mainWindowGlade.get_widget("playlist_treeview")
            
            TARGETS = [
              ('MY_TREE_MODEL_ROW', gtk.TARGET_OTHER_WIDGET, 0),
              ('text/plain', 0, 1),
              ('TEXT', 0, 2),
              ('STRING', 0, 3),
             ]

            
            #self.directoryListWidget.enable_model_drag_dest(TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
            #self.playListWidget.enable_model_drag_dest(TARGETS, gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
            
            self.directoryListWidget.connect("drag_end", self.onDragDir)
            #self.playListWidget.connect("drag-data-get", self.onDragDirReveived)
            self.playListWidget.connect("drag_data_get", self.onDragDirReveived)
            self.playListWidget.connect("drag_data_received", self.onDragDirReveived)
            
            #self.directoryListWidget.connect("drag_leave", self.onDragDir)
            #self.directoryListWidget.connect("drag_motion", self.onDragDir)
            


            #self.directoryListWidget.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
            
            
            self.tagsTreeView = self.mainWindowGlade.get_widget("song_tags_treeview")
            
            self.filterDirectoryEntry = self.mainWindowGlade.get_widget("filter-comboboxentry-entry")
            
            self.radioListTreeView = self.mainWindowGlade.get_widget("radio_list_treeview")
            self.radioUrlEntry = self.mainWindowGlade.get_widget("radio_url_entry")
            
            
            self.musicLibraryFileChooser = self.mainWindowGlade.get_widget("filechooserbutton1")
            
            self.repeatCheckButton = self.mainWindowGlade.get_widget("repeat_checkbutton")
            self.randomCheckButton = self.mainWindowGlade.get_widget("random_checkbutton")
            self.playOnStart = self.mainWindowGlade.get_widget("playonstart_checkbutton")
            self.vpanel = self.mainWindowGlade.get_widget("vpaned1")
            self.hpanel = self.mainWindowGlade.get_widget("hpaned1")
            
            self.vpanel.set_position(FConfiguration().vpanelPostition)
            self.hpanel.set_position(FConfiguration().hpanelPostition)
            
            self.repeatCheckButton.set_active(FConfiguration().isRepeat)
            self.randomCheckButton.set_active(FConfiguration().isRandom)
            self.playOnStart.set_active(FConfiguration().isPlayOnStart)
                      
            self.menuBar = self.mainWindowGlade.get_widget("menubar3")
            self.labelColor = self.mainWindowGlade.get_widget("label31")
            
            self.viewSourceType = self.mainWindowGlade.get_widget("view_combobox")
            cell = gtk.CellRendererText()
            self.viewSourceType.pack_start(cell, True)
            self.viewSourceType.add_attribute(cell, 'text', 0)  
            liststore = gtk.ListStore(str)
            self.viewSourceType.set_model(liststore)
            
            self.viewSourceType.append_text("by artist/album")
            self.viewSourceType.append_text("by radio/stations")
            self.viewSourceType.append_text("by virtual lists")
            self.viewSourceType.set_active(0)
            
            
            
            self.statusBar = self.mainWindowGlade.get_widget("statusbar")
            self.statusBar.push(0, "If you see it Foobnix is working :)")
            
            bgColor = self.labelColor.get_style().bg[gtk.STATE_NORMAL]
            txtColor = self.labelColor.get_style().fg[gtk.STATE_NORMAL]
            
            
            self.menuBar.modify_bg(gtk.STATE_NORMAL, bgColor)
            
            items = self.menuBar.get_children()
            
            #Set god style for main menu
            for item in items:
                current = item.get_children()[0]                
                current.modify_fg(gtk.STATE_NORMAL, txtColor)              
            
            #Directory list panel
            self.root_dir = FConfiguration().mediaLibraryPath
            self.directoryList = DirectoryList(self.root_dir, self.directoryListWidget)
            
            self.playList = PlayList(self.playListWidget)
            
            self.radioListEngine = PlayList(self.radioListTreeView)     
            
            self.playerEngine = PlayerEngine(self.playList)
            
            busController.setPlayerEngine(self.playerEngine)
            
            self.playerEngine.setTimeLabelWidget(self.timeLabelWidget)
            self.playerEngine.setSeekWidget(self.seekWidget)
            self.playerEngine.setWindow(self.window)
            self.playerEngine.setTagsWidget(self.tagsTreeView)
            self.playerEngine.setRandomWidget(self.randomCheckButton)
            self.playerEngine.setRepeatWidget(self.repeatCheckButton)
                           
            
            #self.playerEngine = self.playerEngine.getPlaer()    
            
            if FConfiguration().isPlayOnStart: 
                
                songs = FConfiguration().savedPlayList
                index = FConfiguration().savedSongIndex                  
                self.playList.setSongs(songs, index)
                self.playerEngine.setPlayList(songs)
                self.playerEngine.playIndex(index)
                
               
                
            self.volumeWidget.set_value(FConfiguration().volumeValue * 100)
            self.playerEngine.setVolume(FConfiguration().volumeValue)
            self.radioListEngine.setSongs(FConfiguration().savedRadioList)
        
        def onDragDir(self, treeview, selection):
                selection = treeview.get_selection()
                model, selected = selection.get_selected()
                print selected
                if selected:
                    name = model.get_value(selected, DirectoryList.POS_NAME)
                    path = model.get_value(selected, DirectoryList.POS_PATH)
                    type = model.get_value(selected, DirectoryList.POS_TYPE)               
                    
                    if type == DirectoryList.TYPE_FILE:
                        print "type", type
                        song = Song(name, path, Song.TYPE_FILE)                    
                        self.playList.addSongs([song])
                        self.playerEngine.setPlayList([song])
                        #self.playerEngine.playIndex()
                    elif type == DirectoryList.TYPE_FOLDER:
                        print "type", type                        
                        songs = self.directoryList.getAllSongsByDirectory(path)
                        
                        self.playList.addSongs(songs)
                        self.playerEngine.setPlayList(songs)
                        #self.playerEngine.playIndex()
                        FConfiguration().savedPlayList = songs
                    else:
                        print "type", type
                        song = Song(name, path, Song.TYPE_URL)
                        self.playerEngine.stopState()
                        self.playList.addSongs([song])              
                        self.playerEngine.setPlayList([song])
                        #self.playerEngine.playIndex()
                        #self.playerEngine.playState()
            
        def onDragDirReveived(self, *args):
            print "drag received"                        
        
        def onDragReceived(self, *args):
            print "drug"   
                
        def onFilterDirectoryList(self, widget, key):
            text = self.filterDirectoryEntry.get_text() 
            self.directoryList.filterByName(text)
        def onViewDirecotry(self, *args):
            active_index = self.viewSourceType.get_active()  
            if active_index == 0:
                self.directoryList = DirectoryList(FConfiguration().mediaLibraryPath, self.directoryListWidget)                
            elif active_index == 1:
                PATH = "/mnt/temp/ivan/workspace/python/foobnix/test/radio/"
                list = os.listdir(PATH)
                list = sorted(list)
                self.directoryList.clear()
                for file in list:
                    if not file.endswith(".pls"):
                        continue
                
                    f = open(PATH + file, "r")
                    data = f.read()
                    f.close()
                    
                    plsParser = PLSParser(None)
                    songUrl = plsParser.getStations(data)[0]
                    plsName = file
                    
                    self.directoryList.addSong(Song(plsName + "  [" + songUrl + "]", songUrl, Song.TYPE_URL))                
                    self.radioUrlEntry.set_text("") 
                FConfiguration().savedRadioList = self.radioListEngine.getAllSongs()
            else:
                pass
            
        
        def onRadioPlay(self, widget, event): 
            if is_double_click(event):                
                song = getSongFromWidget(self.radioListTreeView, 0, 3)
                song.type = Song.TYPE_URL
                self.playerEngine.stopState()
                self.radioListEngine.setCursorToSong(song)                  
                self.playerEngine.setPlayList([song])
                self.playerEngine.playIndex()
                self.playerEngine.playState()
        
        def onAddRadio(self, *args):
            songUrl = self.radioUrlEntry.get_text()
            if songUrl:
                plsParser = PLSParser(songUrl)
                
                plsName = plsParser.getPlsName()
                songUrl = plsParser.getFirst()
                
                if plsName and songUrl:                
                    self.radioListEngine.addSong(Song(plsName + "  [" + songUrl + "]", songUrl, Song.TYPE_URL))                
                    self.radioUrlEntry.set_text("") 
                    FConfiguration().savedRadioList = self.radioListEngine.getAllSongs()                 
        
        def onRemoveRadio(self, *args):
            model, iter = self.radioListTreeView.get_selection().get_selected()
            if iter:                
                songUrl = model.get_value(iter, 2)
                model.remove(iter)
                self.radioListEngine.removeSong(Song(songUrl, songUrl))
                FConfiguration().savedRadioList = self.radioListEngine.getAllSongs()
        
        def onRefreshRadio(self, *args):
            
            self.radioListEngine.clear()
            
            PATH = "/mnt/temp/ivan/workspace/python/foobnix/test/radio/"
            list = os.listdir(PATH)
            list = sorted(list)
            for file in list:
                if not file.endswith(".pls"):
                    continue
                
                f = open(PATH + file, "r")
                data = f.read()
                f.close()
                
                plsParser = PLSParser(None)
                songUrl = plsParser.getStations(data)[0]
                plsName = file
                
                self.radioListEngine.addSong(Song(plsName + "  [" + songUrl + "]", songUrl, Song.TYPE_URL))                
                self.radioUrlEntry.set_text("") 
            FConfiguration().savedRadioList = self.radioListEngine.getAllSongs()
                         
            
            pass
        
        def onPlayButton(self, event):
            LOG.debug("Start Playing")           
            self.playerEngine.playState()
            
            
        def onMouseClickSeek(self, widget, event):    
            if event.button == 1:
                width = self.seekWidget.allocation.width          
                x = event.x
                self.playerEngine.seek((x + 0.0) / width * 100);            

            
        def hideWindow(self, *args):
            self.window.hide()
            
        def iconLeftClick(self, *args):
            if self.isShowMainWindow:
                self.window.hide()                
            else:
                self.window.show()
            
            self.isShowMainWindow = not self.isShowMainWindow            
            
        def scrollChanged(self, arg1, event):            
            volume = self.playerEngine.getVolume()            
            if event.direction == gtk.gdk.SCROLL_UP: #@UndefinedVariable
                self.playerEngine.setVolume(volume + 0.1)                
            else:
                self.playerEngine.setVolume(volume - 0.1)
            
            self.volumeWidget.set_value(volume * 100)    
        
        
        def onChooseMusicDirectory(self, path):
            root_direcotry = self.musicLibraryFileChooser.get_filename()            
            self.directoryList.updateDirctoryByPath(root_direcotry)
            FConfiguration().mediaLibraryPath = root_direcotry

        
        def quitApp(self, *args):
            FConfiguration().isRandom = self.randomCheckButton.get_active()
            FConfiguration().isRepeat = self.repeatCheckButton.get_active()
            FConfiguration().vpanelPostition = self.vpanel.get_position()
            FConfiguration().hpanelPostition = self.hpanel.get_position()
            FConfiguration().save()               
            gtk.main_quit()
            
            LOG.debug("configuration save")
        
        def iconRightClick(self, *args):
            self.menuPopUp.show()

        def closePopUP(self, *args):
            self.menuPopUp.hide()
               
        def onPauseButton(self, event):            
            self.playerEngine.pauseState()
                        
        def onStopButton(self, event):
            self.playerEngine.stopState()            
        
        def onPlayNextButton(self, event):
            self.playerEngine.next()
        
        def onPlayPrevButton(self, event):
            self.playerEngine.prev()        
            
        def onVolumeChange(self, widget, obj3, volume):
            FConfiguration().volumeValue = volume / 100            
            self.playerEngine.setVolume(volume / 100)
        
                
        def onSelectDirectoryRow(self, widget, event):                         
            #left double click     
            if is_double_click(event):                
                                
                selection = widget.get_selection()
                model, selected = selection.get_selected()
                if selected:
                    name = model.get_value(selected, DirectoryList.POS_NAME)
                    path = model.get_value(selected, DirectoryList.POS_PATH)
                    type = model.get_value(selected, DirectoryList.POS_TYPE)               
                    
                    if type == DirectoryList.TYPE_FILE:
                        print "type", type
                        song = Song(name, path, Song.TYPE_FILE)                    
                        self.playList.setSongs([song])
                        self.playerEngine.setPlayList([song])
                        self.playerEngine.playIndex()
                    elif type == DirectoryList.TYPE_FOLDER:
                        print "type", type                        
                        songs = self.directoryList.getAllSongsByDirectory(path)
                        
                        self.playList.setSongs(songs)
                        self.playerEngine.setPlayList(songs)
                        self.playerEngine.playIndex()
                        FConfiguration().savedPlayList = songs
                    else:
                        print "type", type
                        song = Song(name, path, Song.TYPE_URL)
                        self.playerEngine.stopState()
                        self.playList.setSongs([song])              
                        self.playerEngine.setPlayList([song])
                        self.playerEngine.playIndex()
                        self.playerEngine.playState()
                        
                        
                        
                        
                        
                    
                               
        
        def onSelectPlayListRow(self, widget, event):
            if is_double_click(event):                
                song = getSongFromWidget(self.playListWidget, PlayList.POS_DESCRIPTIOPN, PlayList.POS_PATH)
                song.type = Song.TYPE_FILE                
                self.playList.setCursorToSong(song)  
                self.playerEngine.setPlayList(FConfiguration().savedPlayList)                        
                self.playerEngine.playSong(song)
                
                                                       

        def onSeek(self, widget, value):            
            self.playerEngine.seek(value);
        
        def showAboutDialog(self, *args):
            self.aboutDialog.show()
            
if __name__ == "__main__":
    
    player = FoobNIX()
    gtk.gdk.threads_init() #@UndefinedVariable
    gtk.main()
