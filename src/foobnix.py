#!/usr/bin/env python
import gtk.glade
import gst
from mouse_utils import is_double_click

import LOG
from file_utils import isDirectory, getSongFromWidget
    
from playlist import PlayList

from confguration import FConfiguration

from player_engine import PlayerEngine
from dirlist import DirectoryList


class FoobNIX:
        def __init__(self): 
            rc_st = ''' 
                        style "menubar-style" { 
                            GtkMenuBar::shadow_type = none
                            GtkMenuBar::internal-padding = 0                                 
                            }                         
                         class "GtkMenuBar" style "menubar-style"
                    '''
            #set custom stile for menubar
            gtk.rc_parse_string(rc_st)   
                        
            self.gladefile = "foobnix.glade" 
            self.mainWindowGlade = gtk.glade.XML(self.gladefile, "foobnixWindow")
            self.popUpGlade = gtk.glade.XML(self.gladefile, "popUpWindow")

            signalsMainWindow = {
                   "on_foobnix_mainWindow_destroy" : self.quitApp,
                   "on_play_button_clicked":self.onPlayButton,
                   "on_pause_button_clicked":self.onPauseButton,
                   "on_stop_button_clicked":self.onStopButton,
                   "on_next_button_clicked":self.onPlayNextButton,
                   "on_prev_button_clicked":self.onPlayPrevButton,
                   "on_volume_hscale_change_value": self.onVolumeChange,
                   "on_button_press_event": self.onMouseClickSeek,
                   "on_directory_treeview_button_press_event":self.onSelectDirectoryRow,
                   "on_playlist_treeview_button_press_event":self.onSelectPlayListRow,
                   "on_filechooserbutton1_current_folder_changed":self.onChooseMusicDirectory,
                   "on_file_quit_activate" :self.quitApp
           }
            
            self.mainWindowGlade.signal_autoconnect(signalsMainWindow)
            
            signalsPopUp = {
                    "on_close_clicked" :self.quitApp,
                    "on_play_clicked" :self.onPlayButton,
                    "on_pause_clicked" :self.onPauseButton,
                    "on_next_clicked" :self.onPlayNextButton,
                    "on_prev_clicked" :self.onPlayPrevButton,
                    "on_cancel_clicked": self.closePopUP
            }
            
            self.popUpGlade.signal_autoconnect(signalsPopUp)
            
            self.icon = gtk.StatusIcon()
            self.icon.set_tooltip("Foobnix music playerEngine")
            self.icon.set_from_stock("gtk-media-play")
            self.icon.connect("activate", self.iconLeftClick)
            self.icon.connect("popup-menu", self.iconRightClick)
            #self.icon.connect("scroll-event", self.scrollChanged)
            
            self.isShowMainWindow = True
                            
            
            self.timeLabelWidget = self.mainWindowGlade.get_widget("seek_progressbar")
            self.window = self.mainWindowGlade.get_widget("foobnixWindow")
            self.window.maximize()
                
            self.menuPopUp = self.popUpGlade.get_widget("popUpWindow")
            
            self.volumeWidget = self.mainWindowGlade.get_widget("volume_hscale")
            
            
            self.seekWidget = self.mainWindowGlade.get_widget("seek_progressbar")
            
            self.directoryListWidget = self.mainWindowGlade.get_widget("direcotry_treeview")
            self.playListWidget = self.mainWindowGlade.get_widget("playlist_treeview")
            self.tagsTreeView = self.mainWindowGlade.get_widget("song_tags_treeview")
            
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
            
            bgColor = self.labelColor.get_style().bg[gtk.STATE_NORMAL]
            txtColor = self.labelColor.get_style().fg[gtk.STATE_NORMAL]
            
            
            self.menuBar.modify_bg(gtk.STATE_NORMAL, bgColor)
            
            items = self.menuBar.get_children()
            
            #Set god style for main menu
            for item in items:
                current = item.get_children()[0]                
                current.modify_fg(gtk.STATE_NORMAL, txtColor)              
            
            #Directory list panel
            root_dir = FConfiguration().mediaLibraryPath
            self.directoryList = DirectoryList(root_dir, self.directoryListWidget)
            self.playList = PlayList(self.playListWidget)     
            
            self.playerEngine = PlayerEngine(self.playList)
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
                
               
                
            self.volumeWidget.set_value(FConfiguration().volumeValue)
            self.playerEngine.setVolume(FConfiguration().volumeValue)
              
           
                   
                
        
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
            volume = self.playerEngine.get_by_name("volume").get_property('volume');            
            if event.direction == gtk.gdk.SCROLL_UP: #@UndefinedVariable
                self.playerEngine.get_by_name("volume").set_property('volume', volume + 0.05)                
            else:
                self.playerEngine.get_by_name("volume").set_property('volume', volume - 0.05)
            
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
            FConfiguration().volumeValue = volume            
            self.playerEngine.setVolume(volume)
                
        def onSelectDirectoryRow(self, widget, event):                         
            #left double click     
            if is_double_click(event):                
                song = getSongFromWidget(self.directoryListWidget, 0, 1)                 
                
                if not isDirectory(song.path):                    
                    self.playList.setSongs([song])
                    self.playerEngine.setPlayList([song])
                    self.playerEngine.playIndex()
                else:                        
                    songs = self.directoryList.getAllSongsByDirectory(song.path)
                    self.playList.setSongs(songs)
                    self.playerEngine.setPlayList(songs)
                    self.playerEngine.playIndex()
        
        def onSelectPlayListRow(self, widget, event):
            if is_double_click(event):                
                song = getSongFromWidget(self.playListWidget, 0, 3)
                                
                self.playList.setCursorToSong(song)                  
                self.playerEngine.playSong(song)
                                                       

        def onSeek(self, widget, value):            
            self.playerEngine.seek(value);
            
if __name__ == "__main__":
    
    player = FoobNIX()
    gtk.gdk.threads_init() #@UndefinedVariable
    gtk.main()