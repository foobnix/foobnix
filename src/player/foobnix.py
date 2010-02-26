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
                self.mainWindow = gtk.glade.XML(self.gladefile, "mainWindow")
                    
                dic = {
               "on_mainWindow_destroy" : gtk.main_quit,
               "on_button1_clicked":self.onPlayButton,
               "on_button2_clicked":self.onPauseButton,
               "on_button3_clicked":self.onStopButton,
               "on_hscale2_change_value": self.onVolumeChange,
               "on_hscale1_change_value": self.onSeek,
               "on_treeview1_button_press_event":self.onSelectDirectoryRow,
               "on_treeview2_button_press_event":self.onSelectPlayListRow,
               }
                
                self.mainWindow.signal_autoconnect(dic)              

                                
                self.songPathWidget = self.mainWindow.get_widget("entry1")
                self.timeLabelWidget = self.mainWindow.get_widget("label7")                
                
                self.volumeWidget = self.mainWindow.get_widget("hscale2")
                self.seekWidget = self.mainWindow.get_widget("hscale1")
                
                self.directoryListWidget = self.mainWindow.get_widget("treeview1")
                self.playListWidget = self.mainWindow.get_widget("treeview2")
                
                
                self.songPathWidget.set_text("/home/ivan/Music/CD1")
                
                self.playerEngine = PlayerEngine()
                self.playerEngine.setTimeLabelWidget(self.timeLabelWidget)
                self.playerEngine.setSeekWidget(self.seekWidget)
                
                self.player = self.playerEngine.getPlaer()
                
                #Directory list panel
                self.directoryList = DirectoryList("/home/ivan/Music/nightwish", self.directoryListWidget)
                self.playList = PlayList(self.playListWidget)                
                
        
        def onPlayButton(self, event):
            LOG.debug("Start Playing")            
            song_path = self.songPathWidget.get_text()                                                               
            self.playerEngine.play(Song(None, song_path))
                        
        def onPauseButton(self, event):            
            self.playerEngine.pause()
                        
        def onStopButton(self, event):
            self.playerEngine.stop()            
            
        def onVolumeChange(self, widget, obj3, volume):
            self.player.get_by_name("volume").set_property('volume', volume / 100)
        
        def onSelectDirectoryRow(self, widget, event):                         
            #left double click     
            if is_double_click(event):                
                song = getSongFromWidget(self.directoryListWidget)                 
                self.songPathWidget.set_text(song.path)
                
                if not isDirectory(song.path):
                    self.playList.addSong(song)
                    self.playerEngine.forcePlay(song)
                else:                        
                    songs = getAllSongsByDirectory(song.path)
                    self.playList.addSongs(songs)
        
        def onSelectPlayListRow(self, widget, event):
            if is_double_click(event):
                self.playListWidget
                song = getSongFromWidget(self.playListWidget)
                self.songPathWidget.set_text(song.path)                    
                self.playerEngine.forcePlay(song)
                                                       

        def onSeek(self, widget, obj3, value):            
            self.playerEngine.seek(value);
            
if __name__ == "__main__":
    
    player = FoobNIX()
    gtk.gdk.threads_init() #@UndefinedVariable
    gtk.main()
