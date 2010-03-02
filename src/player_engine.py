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
from file_utils import getSongPosition
from confguration import FoobNixConf
import LOG


class PlayerEngine():
    def __init__(self, playListEngine):
        self.playListEngine = playListEngine
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
    
        self.stop()
        
        self.playlistSongs = []           
            
        self.currentSong = None
        self.currentIndex = 0;
        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        
    def setTimeLabelWidget(self, timeLabelWidget):
        self.timeLabelWidget = timeLabelWidget
    
    def setSeekWidget(self, seekWidget):
        self.seekWiget = seekWidget
    
    def setWindow(self, mainWindow):
        self.mainWindowGlade = mainWindow   
        
    def setTagsWidget (self, tagsWidget):       
        self.tagsEngine = SongTagsEngine(tagsWidget)
    
    def setVolume(self, volume):
        self.player.get_by_name("volume").set_property('volume', volume / 100)
            
    def setRandomWidget(self, randomCheckButton):
        self.randomCheckButton = randomCheckButton
    
    def setRepeatWidget(self, repeatCheckButton):      
        self.repeatCheckButton = repeatCheckButton
        
    def getPlaer(self):
        return self.player
    
    def forcePlay(self, song):
        self.stop()
        self.play(song)
        self.currentSong = song
        self.currentIndex = getSongPosition(song, self.playlistSongs)
        self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, 0)
        
        try:
            self.mainWindowGlade.set_title(self.currentSong.getFullDescription())
            self.tagsEngine.populate(song)
        except AttributeError:
            LOG.debug("not initialized")
            
        
    def play(self, song=None):
        if song:        
            self.currentSong = song;
            self.runPlaylist()
        else:
            self.runPlaylist()
    
    def next(self):
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
            
            
        self._playCurrentSong(self.currentIndex)
        
    def prev(self):
        self.currentIndex -= 1;
        self._playCurrentSong(self.currentIndex)

    def _playCurrentSong(self, song_index):        
        playListLenght = len(self.playlistSongs)
                
        if 0 <= song_index < playListLenght:
            self.currentSong = self.playlistSongs[self.currentIndex]
            print self.currentSong                     
            self.forcePlay(self.currentSong)
            self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, 0)
            self.playListEngine.setCursorToSong(self.currentSong)
            self.mainWindowGlade.set_title(self.currentSong.getFullDescription())
            self.tagsEngine.populate(self.currentSong)            
            FoobNixConf().savedSongIndex = song_index                
    
    def playList(self, songs, active=0):
        self.playlistSongs = songs;
        if len(songs) == 0:
            return
        
        if active > len(songs):
            active = 0
            
        print len(songs)           
        print active
        self.currentSong = songs[active];
        self.runPlaylist()
        FoobNixConf().savedPlayList = songs    
        
    
    def runPlaylist(self):
        self.player.get_by_name("file-source").set_property("location", self.currentSong.path)        
        self.player.set_state(gst.STATE_PLAYING)        
        self.play_thread_id = thread.start_new_thread(self.play_thread, ()) 
        try:
            self.mainWindowGlade.set_title(self.currentSong.getFullDescription())        
            self.tagsEngine.populate(self.currentSong)    
        except AttributeError:
            LOG.debug("not initialized")
       
    def volume(self, volumeValue):  
        self.player.get_by_name("volumeValue").set_property('volumeValue', volumeValue)  
    
    def seek(self, value):
        pos_current = self.player.query_position(self.time_format, None)[0]
        pos_max = self.player.query_duration(self.time_format, None)[0]           
        
        LOG.debug("Current", pos_current, pos_max)        
        seek_ns = pos_max * value / 100;  
              
        LOG.debug("Set position", seek_ns)
                    
        self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, seek_ns)
        
    def stop(self):        
        self.player.set_state(gst.STATE_NULL)
        self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, 0)
        
    
    def pause(self):
        self.player.set_state(gst.STATE_PAUSED)  
        
    def play_thread(self):
            print "Thread Start"
            play_thread_id = self.play_thread_id
            gtk.gdk.threads_enter() #@UndefinedVariable
            
            self.timeLabelWidget.set_text("00:00 / 00:00")
            
            gtk.gdk.threads_leave() #@UndefinedVariable
    
            while play_thread_id == self.play_thread_id:
                try:
                    time.sleep(0.2)
                    dur_int = self.player.query_duration(self.time_format, None)[0]
                    dur_str = convert_ns(dur_int)
                    gtk.gdk.threads_enter() #@UndefinedVariable
                    
                    self.timeLabelWidget.set_text("00:00 / " + dur_str)                    
                    
                    gtk.gdk.threads_leave() #@UndefinedVariable
                    break
                except:
                    pass
                    
            time.sleep(0.2)
            while play_thread_id == self.play_thread_id:
                pos_int = self.player.query_position(self.time_format, None)[0]
                pos_str = convert_ns(pos_int)
                if play_thread_id == self.play_thread_id:
                    gtk.gdk.threads_enter() #@UndefinedVariable                   
                    
                    self.timePlayingAsString = pos_str + " / " + dur_str
                    self.timePlayingAsPersent = (pos_int + 0.0) / dur_int                    
                    self.timeLabelWidget.set_text(self.timePlayingAsString)
                    self.seekWiget.set_fraction(self.timePlayingAsPersent)
                    
                    gtk.gdk.threads_leave() #@UndefinedVariable
                time.sleep(1)
    
    def on_message(self, bus, message):
            t = message.type
            if t == gst.MESSAGE_EOS:
                print "MESSAGE_EOS"                
                self.play_thread_id = None
                self.player.set_state(gst.STATE_NULL)                
                self.timeLabelWidget.set_text("00:00 / 00:00")
                
                
                gtk.gdk.threads_enter() #@UndefinedVariable
                self.next()               
                gtk.gdk.threads_leave() #@UndefinedVariable
                
                
            elif t == gst.MESSAGE_ERROR:
                print "MESSAGE_ERROR"
                err, debug = message.parse_error()
                print "Error: %s" % err, debug
                self.play_thread_id = None
                self.player.set_state(gst.STATE_NULL)
                
                self.timeLabelWidget.set_text("00:00 / 00:00")
            elif t == gst.MESSAGE_SEGMENT_DONE:
                print "MESSAGE_SEGMENT_DONE"
    
