'''
Created on Mar 2, 2010

@author: ivan
'''
from playerEngine import PlayerEngine
from song import Song
import time
import gtk
from time_utils import convert_ns
import thread
import LOG
import gst

class PlayerModule():
    def __init__(self):
        self.playerEngine = PlayerEngine()
        
        self.timeLabel = "Time label"
        self.playListSongs = []
        self.activeSongIndex = 0 
        
    def setPlayList(self, songs):
        self.playListSongs = songs   
    
    def play(self, active=0):  
        self.playerEngine.playSong(self.playListSongs[active])        
        self.playerThreadId = thread.start_new_thread(self.playThread, ())         
    
    def pause(self):
        self.playerEngine.pause()
        
    def setTimeProgressLabel(self, value):
        gtk.gdk.threads_enter() #@UndefinedVariable            
        self.timeLabel = value 
        LOG.debug(value)
        gtk.gdk.threads_leave() #@UndefinedVariable    
    
    def playThread(self):
        LOG.debug("Start Playing Label")            
        playThreadId = self.playerThreadId            
        self.setTimeProgressLabel("00:00 / 00:00")           

        while playThreadId == self.playerThreadId:
            try:
                time.sleep(0.2)
                durationInt = self.playerEngine.getSongQueryPosition()
                durationStr = convert_ns(durationInt)
                self.setTimeProgressLabel("00:00 / " + durationStr)                
                break
            except:
                pass
             
        time.sleep(0.2)
        while playThreadId == self.playerThreadId:
            pos_int = self.playerEngine.getSongQueryPosition()
            pos_str = convert_ns(pos_int)
            if playThreadId == self.playerThreadId:
                #timePlayingAsPersent = (pos_int + 0.0) / durationInt                   
                self.setTimeProgressLabel(pos_str + " / " + durationStr)   
            time.sleep(1)
