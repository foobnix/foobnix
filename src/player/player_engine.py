'''
Created on Feb 26, 2010

@author: ivan
'''
import gst
from song import Song
class PlayerEngine():
    def __init__(self):
        self.player = gst.Pipeline("player")
        source = gst.element_factory_make("filesrc", "file-source")
        decoder = gst.element_factory_make("mad", "mp3-decoder")
        conv = gst.element_factory_make("audioconvert", "converter")
        sink = gst.element_factory_make("alsasink", "alsa-output")
        volume = gst.element_factory_make("volume", "volume")        
        self.time_format = gst.Format(gst.FORMAT_TIME)
        self.player.add(source, decoder, conv, volume, sink)
        gst.element_link_many(source, decoder, volume, conv, sink)
                        
        
        self.play_thread_id = None
        self.player.set_state(gst.STATE_NULL)
    
    def getPlaer(self):
        return self.player
    
    def play(self, Song):
        self.player.get_by_name("file-source").set_property("location", Song.path)
        self.player.set_state(gst.STATE_PLAYING)        
        
    def stop(self):
        pass
    
    def pause(self):
        pass    
    