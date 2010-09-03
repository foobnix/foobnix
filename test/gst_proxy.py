'''
Created on Sep 2, 2010

@author: ivan
'''
import gst
import gtk
class Player():
    
    def __init__1(self):
        self.player = gst.element_factory_make("playbin", "player")
        #mad = gst.element_factory_make("mad", "mad")
        #source = gst.element_factory_make("souphttpsrc", "source")
               
        #self.player.add(source,mad)
        #gst.element_link_many(source,mad)
        bus = self.player.get_bus()
        bus.connect("message", self.on_message)
    
    def __init__(self):
        self.player = gst.Pipeline("player")
        source = gst.element_factory_make("souphttpsrc", "source")        
        volume = gst.element_factory_make("volume", "volume")
        mad = gst.element_factory_make("mad", "mad")
        audioconvert = gst.element_factory_make("audioconvert", "audioconvert")
        audioresample = gst.element_factory_make("audioresample", "audioresample")
        alsasink = gst.element_factory_make("alsasink", "alsasink")
        #alsasink = gst.element_factory_make("audiotestsrc", "audiotestsrc")
        
        self.player.add(source, mad,volume, audioconvert, audioresample, alsasink)
        gst.element_link_many(source, mad, volume,audioconvert, audioresample, alsasink)
        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
    
    def on_message(self, bus, message):
        print message        
    
        
    def play(self,filepath):
        source  = self.player.get_by_name("source")
        if source:
            print "PLAY PROXY"
            source.set_property("user-agent", "Fooobnix music player")
            source.set_property("automatic-redirect", "false")
            #self.player.get_by_name("source").set_property("proxy", "195.114.128.12:3128")
            source.set_property("proxy", "127.0.0.1:3128")
             
            source.set_property("location", filepath)
        else:
            print "PLAY LOCAL"
            self.player.set_property("uri", filepath)
            
        self.player.get_by_name("volume").set_property('volume', 0.4)
        
        self.player.set_state(gst.STATE_PLAYING)


player = Player()
player.play("http://cs4755.vkontakte.ru/u51615163/audio/576abb0f1562.mp3")
#player.play("http://92.243.94.52:8000/intv_russian_hits-128.mp3")
#player.play("http://217.20.164.163:8014")
print "running"

gtk.main() 