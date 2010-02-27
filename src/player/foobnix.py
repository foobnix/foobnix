#!/usr/bin/env python
import thread, time
import gtk.glade
import gst
from mouse_utils import is_double_click

from player_engine import PlayerEngine
import LOG
from file_utils import getAllSongsByDirectory, isDirectory, getSongFromWidget
from playlist import PlayList
from song import Song
from dirlist import DirectoryList


class FoobNIX:
        def __init__(self):    
                            
                self.gladefile = "foobnix.glade"  
                #self.mainWindow = gtk.glade.XML(self.gladefile, "mainWindow")
                self.mainWindow = gtk.glade.XML(self.gladefile, "foobnixWindow")
                #self.mainWindow = gtk.glade.XML(self.gladefile)
                dic = {
               "on_foobnix_mainWindow_destroy" : gtk.main_quit,
               "on_play_button_clicked":self.onPlayButton,
               "on_pause_button_clicked":self.onPauseButton,
               "on_stop_button_clicked":self.onStopButton,
               "on_next_button_clicked":self.onPlayNextButton,
               "on_prev_button_clicked":self.onPlayPrevButton,
               "on_volume_hscale_change_value": self.onVolumeChange,
               #"on_seek_progressbar_event": self.onSeek,
               "on_directory_treeview_button_press_event":self.onSelectDirectoryRow,
               "on_playlist_treeview_button_press_event":self.onSelectPlayListRow,
               }
                
                self.mainWindow.signal_autoconnect(dic)
                
                self.icon = gtk.StatusIcon()
                self.icon.set_from_stock("gtk-media-play")
                self.icon.connect("activate", self.iconClick)
                self.icon.connect("popup-menu", self.iconPopup)
                self.icon.connect("scroll-event", self.scrollChanged)
                
                self.isShow = True
                                
                
                self.timeLabelWidget = self.mainWindow.get_widget("seek_progressbar")
                self.window = self.mainWindow.get_widget("foobnixWindow")    
                self.window.set_title("title")
                            
                
                self.volumeWidget = self.mainWindow.get_widget("volume_hscale")
                self.seekWidget = self.mainWindow.get_widget("seek_progressbar")
                
                self.directoryListWidget = self.mainWindow.get_widget("direcotry_treeview")
                self.playListWidget = self.mainWindow.get_widget("playlist_treeview")
                
                
                
                
                
                
                #Directory list panel
                self.directoryList = DirectoryList("/home/ivan/Music/!DL", self.directoryListWidget)
                self.playList = PlayList(self.playListWidget)     
                
                self.playerEngine = PlayerEngine(self.playList)
                self.playerEngine.setTimeLabelWidget(self.timeLabelWidget)
                self.playerEngine.setSeekWidget(self.seekWidget)
                
                self.player = self.playerEngine.getPlaer()           
                
        
        def onPlayButton(self, event):
            LOG.debug("Start Playing")            
                                                                           
            self.playerEngine.play()
        
        def hideWindow(self, *args):
            self.window.hide()
            
        def iconClick(self, *args):
            if self.isShow:
                self.window.hide()                
            else:
                self.window.show()
            
            self.isShow = not self.isShow
            print "Icon Click"
            
        def scrollChanged(self, arg1, event):            
            volume = self.player.get_by_name("volume").get_property('volume');            
            if event.direction == gtk.gdk.SCROLL_UP: #@UndefinedVariable
                self.player.get_by_name("volume").set_property('volume', volume + 0.05)                
            else:
                self.player.get_by_name("volume").set_property('volume', volume - 0.05)
            
            self.volumeWidget.set_value(volume * 100)    
            print volume
                        
                            
        def iconPopup(self,*args):
            print "Icon PopUp"            
            gtk.main_quit()
                        
        def onPauseButton(self, event):            
            self.playerEngine.pause()
                        
        def onStopButton(self, event):
            self.playerEngine.stop()            
        
        def onPlayNextButton(self, event):
            self.playerEngine.next()
        
        def onPlayPrevButton(self, event):
            self.playerEngine.prev()        
            
        def onVolumeChange(self, widget, obj3, volume):
            self.player.get_by_name("volume").set_property('volume', volume / 100)
        
        def onSelectDirectoryRow(self, widget, event):                         
            #left double click     
            if is_double_click(event):                
                song = getSongFromWidget(self.directoryListWidget,0,1)                 
                
                
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
                song = getSongFromWidget(self.playListWidget,0,2)
                
                
                self.playList.setCursorToSong(song)                    
                
                self.playerEngine.forcePlay(song)
                                                       

        def onSeek(self, widget, value):            
            self.playerEngine.seek(value);
            
if __name__ == "__main__":
    
    player = FoobNIX()
    gtk.gdk.threads_init() #@UndefinedVariable
    gtk.main()
