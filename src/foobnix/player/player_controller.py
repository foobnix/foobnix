'''
Created on Mar 11, 2010

@author: ivan
'''
import gst
import gtk
import time

import thread
from foobnix.util.time_utils import convert_ns
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

    def registerPlaylistCntr(self, playlistCntr):
        self.playlistCntr = playlistCntr

    def registerWidgets(self, widgets):
        self.widgets = widgets

    def playSong(self, song):
        print "play song"
                
        self.stopState()
                
        self.player.set_property("uri", "file://" + song.path)
        self.playerThreadId = thread.start_new_thread(self.playThread, ())
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
        #playbin2.connect('about-to-finish', self.next)
        return playbin2       
    
    
    def next(self, *a):
        song = self.playlistCntr.getNextSong()        
        self.playSong(song)
    
    def prev(self):
        song = self.playlistCntr.getPrevSong()        
        self.playSong(song)
    
    def setVolume(self, volumeValue): 
        self.player.set_property('volume', volumeValue + 0.0)  
    
    def setSeek(self, persentValue):        
        pos_max = self.player.query_duration(self.time_format, None)[0]           
        seek_ns = pos_max * persentValue / 100;  
        self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, seek_ns)
    
    def playThread(self):
        print "Start Thread"        
        play_thread_id = self.playerThreadId
        gtk.gdk.threads_enter()#@UndefinedVariable
        self.widgets.seekBar.set_text("00:00 / 00:00 init")
        gtk.gdk.threads_leave() #@UndefinedVariable

        while play_thread_id == self.playerThreadId:
            try:
                print "Try"
                time.sleep(0.2)
                dur_int = self.player.query_duration(self.time_format, None)[0]
                #self.currentSong= dur_int / 1000000000
                dur_str = convert_ns(dur_int)
                gtk.gdk.threads_enter() #@UndefinedVariable
                
                self.widgets.seekBar.set_text("00:00 / " + dur_str)                    
                
                gtk.gdk.threads_leave() #@UndefinedVariable
                break
            except:
                print "Error"
                pass
                
        time.sleep(0.2)
        while play_thread_id == self.playerThreadId:
            pos_int = self.player.query_position(self.time_format, None)[0]
            
            pos_str = convert_ns(pos_int)
            if play_thread_id == self.playerThreadId:
                gtk.gdk.threads_enter() #@UndefinedVariable                   
                
                timeStr = pos_str + " / " + dur_str
                timePersent = (pos_int + 0.0) / dur_int
                              
                self.widgets.seekBar.set_text(timeStr)
                self.widgets.seekBar.set_fraction(timePersent)
                
                gtk.gdk.threads_leave() #@UndefinedVariable
            time.sleep(1)
    
        

    def onBusMessage(self, bus, message):
        type = message.type
        if type == gst.MESSAGE_EOS:
            
            print "MESSAGE_EOS"                
            self.stopState()
            self.playerThreadId = None
            
            self.next()
                            

        elif type == gst.MESSAGE_ERROR:
            print "MESSAGE_ERROR"
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.stopState()
            self.playerThreadId = None
            
            
    