'''
Created on Mar 2, 2010

@author: ivan
'''
import gst
import LOG
class MP3PlayerEngine():
    def __init__(self): 
        """ Create MP3 Player """
        self.playerEngine = gst.Pipeline("playerEngine")
        source = gst.element_factory_make("filesrc", "file-source")
        decoder = gst.element_factory_make("mad", "mp3-decoder")
        conv = gst.element_factory_make("audioconvert", "converter")
        sink = gst.element_factory_make("alsasink", "alsa-output")
        volume = gst.element_factory_make("volume", "volume")       
        
        self.playerEngine.add(source, decoder, conv, volume, sink)
        gst.element_link_many(source, decoder, volume, conv, sink)
            
        bus = self.playerEngine.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)  
        
        LOG.debug("Initialize MP3 playerEngine") 
    
    def getEngine(self):
        return self.playerEngine  
    
    def on_message(self, bus, message):
        message_type = message.type
        if message_type == gst.MESSAGE_EOS:
            print "MESSAGE End of Song"              
            self.playerEngine.set_state(gst.STATE_NULL)                
        elif message_type == gst.MESSAGE_ERROR:
            print "MESSAGE_ERROR"
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.playerEngine.set_state(gst.STATE_NULL)
        elif message_type == gst.MESSAGE_SEGMENT_DONE:
            print "MESSAGE_SEGMENT_DONE" 
