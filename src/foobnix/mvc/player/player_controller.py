'''
Created on Mar 11, 2010

@author: ivan
'''
import gst
class PlayerController:
    def __init__(self):
        self.player = self.playerLocal()
        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.onBusMessage)
        
        self.songs = []
        self.cIndex = 0
        
        self.time_format = gst.Format(gst.FORMAT_TIME)
    pass

    def playSong(self, song):
        print "play song"
        self.stopState()
        self.player.set_property("uri", "file://" + song.path)
        self.playState()

    def pauseState(self):
        self.player.set_state(gst.STATE_PAUSED)  
    
    def playState(self):
        self.player.set_state(gst.STATE_PLAYING)
    
    def stopState(self):
        self.player.set_state(gst.STATE_NULL)

    def playerHTTP(self):
        print "Player For remote files"
        playbin = gst.element_factory_make("playbin", "player")
        return playbin

    def playerLocal(self):
        print "Player Local Files"
        playbin2 = gst.element_factory_make("playbin2", "player")
        playbin2.connect('about-to-finish', self.onFinishSong)
        return playbin2       
    
    
    def onFinishSong(self, *a):
        pass

    def onBusMessage(self, bus, message):
        type = message.type
        if type == gst.MESSAGE_EOS:
            print "MESSAGE_EOS"                
            self.playerThreadId = None
            self.stopState()                

        elif type == gst.MESSAGE_ERROR:
            print "MESSAGE_ERROR"
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.playerThreadId = None
            self.stopState()
            
    