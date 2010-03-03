'''
Created on Feb 26, 2010

@author: ivan
'''
import gst
import time
import thread
from time_utils import convert_ns
import gtk
from songtags_engine import SongTagsEngine
import random
from file_utils import getSongPosition, getExtenstion
from confguration import FConfiguration
import LOG


class PlayerEngine():
    def __init__(self, playListEngine):
        self.playListEngine = playListEngine
        
        self.playerEngine = gst.element_factory_make("playbin2", "player")

        #Song represents
        self.playlistSongs = []
        self.currentSong = None
        self.currentIndex = 0;
        
        bus = self.playerEngine.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.onMessage)
        
        self.time_format = gst.Format(gst.FORMAT_TIME)
      
        
    def setTimeLabelWidget(self, timeLabelWidget):
        self.timeLabelWidget = timeLabelWidget
    
    def setSeekWidget(self, seekWidget):
        self.seekWiget = seekWidget
    
    def setWindow(self, mainWindow):
        self.mainWindowGlade = mainWindow   
        
    def setTagsWidget (self, tagsWidget):       
        self.tagsEngine = SongTagsEngine(tagsWidget)
    
    def setVolume(self, volume):
        self.playerEngine.set_property('volume', volume / 100)
            
    def setRandomWidget(self, randomCheckButton):
        self.randomCheckButton = randomCheckButton
    
    def setRepeatWidget(self, repeatCheckButton):      
        self.repeatCheckButton = repeatCheckButton
        
    def getPlaer(self):
        return self.playerEngine
        
    def setPlayList(self, songs):
        self.playlistSongs = songs
        self.currentIndex = 0
        if songs and len(songs) > 0:
            self.currentSong = songs[0]
            
        
    def playIndex(self, index=0):
        self.stopState()
        self.currentIndex = index         
        self._playCurrentSong()
    
    def playSong(self, song):
        self.stopState()
        self.currentIndex = getSongPosition(song, self.playlistSongs)
        self.currentSong = song         
        self._playCurrentSong()    
        
    
    def next(self):
        self.stopState()
        self.currentIndex += 1
        
        '''if random enable:'''
        if(self.randomCheckButton.get_active()):
            rand = random.randint(1, len(self.playlistSongs))            
            self.currentIndex = rand
        
        '''Play First Song when repeat'''    
        if(self.repeatCheckButton.get_active()):
            print "repeat"            
            if self.currentIndex >= len(self.playlistSongs):
                self.currentIndex = 0   
            
            
        self._playCurrentSong()
        
    def prev(self):
        self.stopState()
        self.currentIndex -= 1;
        self._playCurrentSong()

    def _playCurrentSong(self):        
        playListLenght = len(self.playlistSongs)
                
        if 0 <= self.currentIndex < playListLenght:
            self.currentSong = self.playlistSongs[self.currentIndex]
            print "_playCurrentSong" + self.currentSong.path                    
            self.playerEngine.set_property("uri", "file://" + self.currentSong.path)
            self.playState()
            self.playerThreadId = thread.start_new_thread(self.playThread, ())
            self.playerEngine.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, 0)
            self.playListEngine.setCursorToSong(self.currentSong)
            self.mainWindowGlade.set_title(self.currentSong.getFullDescription())
            self.tagsEngine.populate(self.currentSong)            
            FConfiguration().savedSongIndex = self.currentIndex                
    
   
       
    
    def volume(self, volumeValue):  
        self.playerEngine.get_by_name("volumeValue").set_property('volumeValue', volumeValue)  
    
    def seek(self, value):
        pos_current = self.playerEngine.query_position(self.time_format, None)[0]
        pos_max = self.playerEngine.query_duration(self.time_format, None)[0]           
        
        LOG.debug("Current", pos_current, pos_max)        
        seek_ns = pos_max * value / 100;  
              
        LOG.debug("Set position", seek_ns)
                    
        self.playerEngine.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, seek_ns)
        
    def stopState(self):        
        self.playerEngine.set_state(gst.STATE_NULL)
        self.playerEngine.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, 0)
        
    
    def pauseState(self):
        self.playerEngine.set_state(gst.STATE_PAUSED)  
    
    def playState(self):
        self.playerEngine.set_state(gst.STATE_PLAYING)
        
        
    def playThread(self):
            
            play_thread_id = self.playerThreadId
            gtk.gdk.threads_enter() #@UndefinedVariable
            
            self.timeLabelWidget.set_text("00:00 / 00:00")
            
            gtk.gdk.threads_leave() #@UndefinedVariable
    
            while play_thread_id == self.playerThreadId:
                try:
                    time.sleep(0.2)
                    dur_int = self.playerEngine.query_duration(self.time_format, None)[0]                    
                    self.currentSong.second = dur_int / 1000000000
                    dur_str = convert_ns(dur_int)
                    gtk.gdk.threads_enter() #@UndefinedVariable
                    
                    self.timeLabelWidget.set_text("00:00 / " + dur_str)                    
                    
                    gtk.gdk.threads_leave() #@UndefinedVariable
                    break
                except:
                    pass
                    
            time.sleep(0.2)
            while play_thread_id == self.playerThreadId:
                pos_int = self.playerEngine.query_position(self.time_format, None)[0]
                pos_str = convert_ns(pos_int)
                if play_thread_id == self.playerThreadId:
                    gtk.gdk.threads_enter() #@UndefinedVariable                   
                    
                    self.timePlayingAsString = pos_str + " / " + dur_str
                    self.timePlayingAsPersent = (pos_int + 0.0) / dur_int                    
                    self.timeLabelWidget.set_text(self.timePlayingAsString)
                    self.seekWiget.set_fraction(self.timePlayingAsPersent)
                    
                    gtk.gdk.threads_leave() #@UndefinedVariable
                time.sleep(1)
    
    def onMessage(self, bus, message):
        
        type = message.type
        if type == gst.MESSAGE_EOS:
            print "MESSAGE_EOS"                
            self.playerThreadId = None
            self.playerEngine.set_state(gst.STATE_NULL)                
            self.timeLabelWidget.set_text("00:00 / 00:00")
            
            
            gtk.gdk.threads_enter() #@UndefinedVariable
            self.next()               
            gtk.gdk.threads_leave() #@UndefinedVariable
            
            
        elif type == gst.MESSAGE_ERROR:
            print "MESSAGE_ERROR"
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.playerThreadId = None
            self.playerEngine.set_state(gst.STATE_NULL)
            
            self.timeLabelWidget.set_text("00:00 / 00:00")
        elif type == gst.MESSAGE_SEGMENT_DONE:
            print "MESSAGE_SEGMENT_DONE"

