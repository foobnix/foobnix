import gst
import time
import urllib

class Radio:
    def __init__(self):
        radio = "http://www.di.fm/mp3/chilloutdreams.pls"                
        response = urllib.urlopen(radio)           
        print response.read()
        
        self.playerEngine = gst.element_factory_make("playbin2", "player")        
        self.playerEngine.set_property("uri", "http://cs4406.vkontakte.ru/u17609241/audio/9cc0a3e6bd9a.mp3")        
        self.playerEngine.set_state(gst.STATE_PLAYING)
        time.sleep(1)
        

radio = Radio()

time.sleep(115)
print "finish"
