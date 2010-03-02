'''
Created on Mar 2, 2010

@author: ivan
'''
import gst
from mp3PlayerEngine import MP3PlayerEngine
import LOG

class PlayerEngine:
    def __init__(self):
        mp3Player = MP3PlayerEngine()
        self.playerEngine = mp3Player.getEngine()        
        LOG.debug("Initialize Player Engine ")
        self.stop() 
              
        
    def playSong(self, song):
        LOG.debug("Set song ", song)
        self.playerEngine.get_by_name("file-source").set_property("location", song.path)
        self.play()
    
    def play(self):
        LOG.debug("Play")                
        self.playerEngine.set_state(gst.STATE_PLAYING)
        
    def pause(self):
        LOG.debug("Pause")
        self.playerEngine.set_state(gst.STATE_PAUSED)  
    
    def stop(self):
        LOG.debug("Stop")
        self.playerEngine.set_state(gst.STATE_NULL)
    
    def setSeek(self, value):
        LOG.debug("Seek ", value)     
        self.playerEngine.seek_simple(gst.Format(gst.FORMAT_TIME), gst.SEEK_FLAG_FLUSH, value)
    
    def setVolume(self, volume):
        LOG.debug("Volume ", volume)
        self.playerEngine.get_by_name("volume").set_property('volume', volume)    
    
    def getSongQueryPosition(self):
        return self.playerEngine.query_position(gst.Format(gst.FORMAT_TIME), None)[0]
    



