import gst
import time
import urllib

class Radio:
    def __init__(self):
  
        print buffer 
        
        self.playerEngine = gst.element_factory_make("playbin", "player")
        #q1 = gst.element_factory_make("queue", "q1")
        #G1 = gst.element_factory_make("giostreamsrc", "src")
        #self.playerEngine.add(q1)
        #self.playerEngine.add(G1)

                
        #self.playerEngine.set_property("uri", "http://cs4406.vkontakte.ru/u17609241/audio/9cc0a3e6bd9a.mp3")
        self.playerEngine.set_property("uri", "http://scfire-ntc-aa07.stream.aol.com:80/stream/1003")
                
        self.playerEngine.set_state(gst.STATE_PLAYING)
        bus = self.playerEngine.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.onMessage)

    def onMessage(self, bus, message):        
        type = message.type
        print type
         
     
        
print "Start"
radio = Radio()

time.sleep(111115)
print "finish"
