#!/usr/bin/env python
import thread, time
import gtk.glade
import gst
from mouse_utils import is_double_click

from player_engine import PlayerEngine
import LOG
from file_utils import getAllSongsByDirectory, isDirectory, getSongFromWidget, \
    getSongPosition
from playlist import PlayList
from song import Song
from dirlist import DirectoryList
from confguration import FoobNixConf
from songtags_engine import SongTagsEngine


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
                #self.mainWindowGlade = gtk.glade.XML(self.gladefile, "mainWindowGlade")
                self.mainWindowGlade = gtk.glade.XML(self.gladefile, "foobnixWindow")
                self.popUpGlade = gtk.glade.XML(self.gladefile, "popUpWindow")
                
                #self.mainWindowGlade = gtk.glade.XML(self.gladefile)
                dic = {
               "on_foobnix_mainWindow_destroy" : self.hideWindow,
               "on_play_button_clicked":self.onPlayButton,
               "on_pause_button_clicked":self.onPauseButton,
               "on_stop_button_clicked":self.onStopButton,
               "on_next_button_clicked":self.onPlayNextButton,
               "on_prev_button_clicked":self.onPlayPrevButton,
               "on_volume_hscale_change_value": self.onVolumeChange,
               "on_scroll_event": self.onScrollSeek,
               "on_button_press_event": self.onMouseClickSeek,
               "on_directory_treeview_button_press_event":self.onSelectDirectoryRow,
               "on_playlist_treeview_button_press_event":self.onSelectPlayListRow,
               "on_filechooserbutton1_current_folder_changed":self.onChooseMusicDirectory
               }
                
                self.mainWindowGlade.signal_autoconnect(dic)
                
                dicPopUp = {
                "on_close_clicked" :self.quitApp,
                "on_play_clicked" :self.onPlayButton,
                "on_pause_clicked" :self.onPauseButton,
                "on_next_clicked" :self.onPlayNextButton,
                "on_prev_clicked" :self.onPlayPrevButton,
                "on_cancel_clicked": self.closePopUP
                            }
                self.popUpGlade.signal_autoconnect(dicPopUp)
                
                self.icon = gtk.StatusIcon()
                self.icon.set_tooltip("Foobnix music player")
                self.icon.set_from_stock("gtk-media-play")
                self.icon.connect("activate", self.iconClick)
                
                menu = gtk.Menu()

                for i in range(3):
                # Copy the names to the buf.
                    buf = "Test-undermenu - %d" % i
        
                    # Create a new menu-item with a name...
                    menu_items = gtk.MenuItem(buf)
        
                # ...and add it to the menu.
                    menu.append(menu_items)
                self.icon.connect("popup-menu", self.iconPopup, menu)
                #self.icon.connect("scroll-event", self.scrollChanged)
                
                self.isShowMainWindow = True
                                
                
                self.timeLabelWidget = self.mainWindowGlade.get_widget("seek_progressbar")
                self.window = self.mainWindowGlade.get_widget("foobnixWindow")    
                self.popUp = self.popUpGlade.get_widget("popUpWindow")
                
                            
                
                self.volumeWidget = self.mainWindowGlade.get_widget("volume_hscale")
                
                
                self.seekWidget = self.mainWindowGlade.get_widget("seek_progressbar")
                
                self.directoryListWidget = self.mainWindowGlade.get_widget("direcotry_treeview")
                self.playListWidget = self.mainWindowGlade.get_widget("playlist_treeview")
                self.tagsTreeView = self.mainWindowGlade.get_widget("song_tags_treeview")
                
                self.musicLibraryFileChooser = self.mainWindowGlade.get_widget("filechooserbutton1")
                
                self.repeatCheckButton = self.mainWindowGlade.get_widget("repeat_checkbutton")
                self.randomCheckButton = self.mainWindowGlade.get_widget("random_checkbutton")
                self.playOnStart = self.mainWindowGlade.get_widget("playonstart_checkbutton")
                               
                
                
                self.repeatCheckButton.set_active(FoobNixConf().isRepeat)
                self.randomCheckButton.set_active(FoobNixConf().isRandom)
                self.playOnStart.set_active(FoobNixConf().isPlayOnStart)
                          
                self.menuBar = self.mainWindowGlade.get_widget("menubar3")
                self.labelColor = self.mainWindowGlade.get_widget("label31")
                
                bg_color = self.labelColor.get_style().bg[gtk.STATE_NORMAL]
                txt_color = self.labelColor.get_style().fg[gtk.STATE_NORMAL]
                
                
                self.menuBar.modify_bg(gtk.STATE_NORMAL, bg_color)
                
                items = self.menuBar.get_children()
                #print self.menuBar.shadow_type(gtk.SHADOW_NONE)
               
                
                for item in items:
                    current = item.get_children()[0]                
                    current.modify_fg(gtk.STATE_NORMAL, txt_color)              
                
                
                #Directory list panel
                root_dir = FoobNixConf().mediaLibraryPath
                self.directoryList = DirectoryList(root_dir, self.directoryListWidget)
                self.playList = PlayList(self.playListWidget)     
                
                self.playerEngine = PlayerEngine(self.playList)
                self.playerEngine.setTimeLabelWidget(self.timeLabelWidget)
                self.playerEngine.setSeekWidget(self.seekWidget)
                self.playerEngine.setWindow(self.window)
                self.playerEngine.setTagsWidget(self.tagsTreeView)
                self.playerEngine.setRandomWidget(self.randomCheckButton)
                self.playerEngine.setRepeatWidget(self.repeatCheckButton)
                               
                
                self.player = self.playerEngine.getPlaer()    
                
                if FoobNixConf().isPlayOnStart:                    
                    self.playerEngine.playList(FoobNixConf().savedPlayList, FoobNixConf().savedSongIndex)
                
                self.volumeWidget.set_value(FoobNixConf().volumeValue)
                self.playerEngine.setVolume(FoobNixConf().volumeValue)
                       
                
        
        def onPlayButton(self, event):
            LOG.debug("Start Playing")            
                                                                           
            self.playerEngine.play()
            
        def onScrollSeek(self, *events):
            print "scroll"
            
        def onMouseClickSeek(self, widget, event):    
            if event.button == 1:
                width = self.seekWidget.allocation.width          
                x = event.x
                self.playerEngine.seek((x + 0.0) / width * 100);            

            
        def hideWindow(self, *args):
            self.window.hide()
            
        def iconClick(self, *args):
            if self.isShowMainWindow:
                self.window.hide()                
            else:
                self.window.show_all()
            
            self.isShowMainWindow = not self.isShowMainWindow
            print "Icon Click"
            
        def scrollChanged(self, arg1, event):            
            volume = self.player.get_by_name("volume").get_property('volume');            
            if event.direction == gtk.gdk.SCROLL_UP: #@UndefinedVariable
                self.player.get_by_name("volume").set_property('volume', volume + 0.05)                
            else:
                self.player.get_by_name("volume").set_property('volume', volume - 0.05)
            
            self.volumeWidget.set_value(volume * 100)    
            print volume
        
        
        def onChooseMusicDirectory(self, path):
            root_direcotry = self.musicLibraryFileChooser.get_filename()
            LOG.debug(root_direcotry)
            self.directoryList.updateDirctoryByPath(root_direcotry)
            FoobNixConf().mediaLibraryPath = root_direcotry

        
        def quitApp(self, *args):
            FoobNixConf().isRandom = self.randomCheckButton.get_active()
            FoobNixConf().isRepeat = self.repeatCheckButton.get_active()
            FoobNixConf().save()               
            gtk.main_quit()
            #FoobNixConf.save()
            LOG.debug("configuration save")
                            
              
        
        def iconPopup(self, arg1, arg3, widget, event):
            self.popUp.show()

        def closePopUP(self, *args):
            self.popUp.hide()
               
        def onPauseButton(self, event):            
            self.playerEngine.pause()
                        
        def onStopButton(self, event):
            self.playerEngine.stop()            
        
        def onPlayNextButton(self, event):
            self.playerEngine.next()
        
        def onPlayPrevButton(self, event):
            self.playerEngine.prev()        
            
        def onVolumeChange(self, widget, obj3, volume):
            FoobNixConf().volumeValue = volume            
            self.playerEngine.setVolume(volume)
        
        
        
        def onSelectDirectoryRow(self, widget, event):                         
            #left double click     
            if is_double_click(event):                
                song = getSongFromWidget(self.directoryListWidget, 0, 1)                 
                
                
                if not isDirectory(song.path):
                    self.playList.addSong(song)
                    self.playerEngine.forcePlay(song)
                else:                        
                    songs = getAllSongsByDirectory(song.path)
                    self.playList.addSongs(songs)
                    self.playerEngine.playList(songs)
        
        def onSelectPlayListRow(self, widget, event):
            if is_double_click(event):
                self.playListWidget
                song = getSongFromWidget(self.playListWidget, 0, 2)
                
                
                self.playList.setCursorToSong(song)                    
                
                self.playerEngine.forcePlay(song)
                                                       

        def onSeek(self, widget, value):            
            self.playerEngine.seek(value);
            
if __name__ == "__main__":
    
    player = FoobNIX()
    gtk.gdk.threads_init() #@UndefinedVariable
    gtk.main()
