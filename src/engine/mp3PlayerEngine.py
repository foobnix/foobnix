'''
Created on Mar 2, 2010

@author: ivan
'''
import gst
import LOG
class MP3PlayerEngine():
    def __init__(self): 
        """ Create MP3 Player """
        self.player = gst.Pipeline("player")
        source = gst.element_factory_make("filesrc", "file-source")
        decoder = gst.element_factory_make("mad", "mp3-decoder")
        conv = gst.element_factory_make("audioconvert", "converter")
        sink = gst.element_factory_make("alsasink", "alsa-output")
        volume = gst.element_factory_make("volume", "volume")       
        
        self.player.add(source, decoder, conv, volume, sink)
        gst.element_link_many(source, decoder, volume, conv, sink)
            
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)  
        
        LOG.debug("Initialize MP3 player") 
    
    def getEngine(self):
        return self.player  
    
    def on_message(self, bus, message):
        message_type = message.type
        if message_type == gst.MESSAGE_EOS:
            print "MESSAGE End of Song"              
            self.player.set_state(gst.STATE_NULL)                
        elif message_type == gst.MESSAGE_ERROR:
            print "MESSAGE_ERROR"
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.player.set_state(gst.STATE_NULL)
        elif message_type == gst.MESSAGE_SEGMENT_DONE:
            print "MESSAGE_SEGMENT_DONE" 
