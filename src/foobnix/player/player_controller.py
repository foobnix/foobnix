'''
Created on Mar 11, 2010

@author: ivan
'''
import os
import gst
import gtk
import time
import urllib

import thread
from foobnix.util.time_utils import convert_ns
from foobnix.model.entity import CommonBean
from foobnix.util import LOG
from foobnix.base import BaseController
from foobnix.base import SIGNAL_RUN_FIRST, TYPE_NONE, TYPE_PYOBJECT
from foobnix.thirdparty import pylast
from foobnix.util.configuration import FConfiguration
from foobnix.online.dowload_util import dowload_song_thread
from foobnix.util.plsparser import get_radio_source


username = FConfiguration().lfm_login
password_hash = pylast.md5(FConfiguration().lfm_password)

try:
    lastfm = pylast.get_lastfm_network(username=username, password_hash=password_hash)
    scrobler = lastfm.get_scrobbler("fbx", "1.0")
except:
    lastfm = None
    scrobler = None
    LOG.error("last.fm or scrobler connection error")
    

class PlayerController(BaseController):
    MODE_RADIO = "RADIO"
    MODE_PLAY_LIST = "PLAY_LIST"
    MODE_ONLINE_LIST = "ONLINE_LIST"
    
    
    __gsignals__ = {
        'song_playback_started' : (SIGNAL_RUN_FIRST, TYPE_NONE, (TYPE_PYOBJECT,))
    }
    
        
    def __init__(self):
        BaseController.__init__(self)
        self.player = self.playerLocal()
        
        self.songs = []
        self.cIndex = 0
        
        self.time_format = gst.Format(gst.FORMAT_TIME)
        self.volume = 0
        self.mode = self.MODE_PLAY_LIST
        
        # TODO: rename playState() to play() and remove this hack
        self.play = self.playState
        self.pause = self.pauseState
        

    def set_mode(self, mode):
        self.mode = mode 

    def registerPlaylistCntr(self, playlistCntr):
        self.playlistCntr = playlistCntr
    
    def registerOnlineCntr(self, onlineCntr):
        self.onlineCntr = onlineCntr

    def registerWidgets(self, widgets):
        self.widgets = widgets

    count = 0
    def playSong(self, song):
        self.song = song
        print "play song"
                
        self.stopState()
        
        if not song:
            LOG.info("NULL song can't playing")
            return
        
        print "Path before", song.path
        #Try to set resource
        if song.path == None or song.path == "":
            print "PL CNTR SET PATH"
            self.onlineCntr.setSongResource(song)
        
        print "Path after", song.path
        if song.path == None or song.path == "":
            self.count += 1
            print "SONG NOT FOUND", song.name
            print "Count is", self.count
            if self.count > 5:
                return
            return self.next()
        
        self.count = 0
        self.widgets.setLiric(song)
            
        print "Type", song.type
       
        print "MODE", self.mode
        print "Name", song.name
        
        if  song.type == CommonBean.TYPE_MUSIC_FILE:
            self.player = self.playerLocal()
            uri = 'file://' + urllib.pathname2url(song.path)
            if os.name == 'nt':
                uri = 'file:' + urllib.pathname2url(song.path)
            self.player.set_property("uri", uri)
            self.playerThreadId = thread.start_new_thread(self.playThread, (song,))
        elif song.type == CommonBean.TYPE_RADIO_URL:
            print "URL PLAYING", song.path
            self.player = self.playerHTTP()    
            path = get_radio_source(song.path)                    
            self.player.set_property("uri", path)
            self.widgets.seekBar.set_text("Url Playing...")
        elif song.type == CommonBean.TYPE_MUSIC_URL:
            print "URL PLAYING", song.path
            self.player = self.playerHTTP()                        
            self.player.set_property("uri", song.path)            
            self.playerThreadId = thread.start_new_thread(self.playThread, (song,))
        else:
            self.widgets.seekBar.set_text("Error playing...")
            return
                
        self.playState()
        self.setVolume(self.volume)
        self.emit('song_playback_started', song)
                
    
    def pauseState(self, *args):
        self.player.set_state(gst.STATE_PAUSED)  
    
    def playState(self, *args):
        self.player.set_state(gst.STATE_PLAYING)
    
    def stopState(self):
        if not self.player:
            self.player = self.playerLocal()    
        self.setSeek(0.0)
        self.widgets.seekBar.set_fraction(0.0)
        self.widgets.seekBar.set_text("00:00 / 00:00")
        self.playerThreadId = None
        self.player.set_state(gst.STATE_NULL)
    
    def volume_up(self, *args):
        self.setVolume(self.getVolume() + 0.05)

    def volume_down(self, *args):
        self.setVolume(self.getVolume() - 0.05)
    
    def setVolume(self, volumeValue): 
        self.volume = volumeValue
        self.player.set_property('volume', volumeValue + 0.0)
    def getVolume(self):
        return self.volume
    
    def playerHTTP(self):
        LOG.info("Player For remote files")
        self.playbin = gst.element_factory_make("playbin", "player")  
        bus = self.playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.onBusMessage)     
        return self.playbin

    def playerLocal(self):
        LOG.info("Player Local Files")
        self.playbin = gst.element_factory_make("playbin2", "player")
        bus = self.playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.onBusMessage)
        
        return self.playbin       
    
    
    def next(self, *args):
        if self.mode == self.MODE_ONLINE_LIST:
            song = self.onlineCntr.getNextSong()
        else:
            song = self.playlistCntr.getNextSong()
        
        if song:
            self.playSong(song)
        
    
    def prev(self, *args):
        if self.mode == self.MODE_ONLINE_LIST:
            song = self.onlineCntr.getPrevSong()   
        else:
            song = self.playlistCntr.getPrevSong()  
           
        self.playSong(song)
    
    
    def _isStatusNull(self):
        return self.player.get_state()[1] == gst.STATE_NULL
    
    def _get_state(self):
        return self.player.get_state()[1]
    
    def setSeek(self, persentValue):  
        if self._isStatusNull():
            self.playerThreadId = None
            return None
        pos_max = 1
        try:
            pos_max = self.player.query_duration(self.time_format, None)[0]
        except:
            LOG.error("Seek for new position error")
            
        seek_ns = pos_max * persentValue / 100;  
        self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, seek_ns)
    
    def playThread(self, song=None):
        LOG.info("Starts playing thread")        
        flag = True
        is_scrobled = False
        play_thread_id = self.playerThreadId
        gtk.gdk.threads_enter()#@UndefinedVariable        
        self.widgets.seekBar.set_text("00:00 / 00:00")
        gtk.gdk.threads_leave() #@UndefinedVariable
        sec = 0;

        while play_thread_id == self.playerThreadId:
            try:
                print "Try"
                time.sleep(0.2)
                dur_int = self.player.query_duration(self.time_format, None)[0]
                duration_sec = dur_int / 1000000000
                dur_str = convert_ns(dur_int)
                gtk.gdk.threads_enter() #@UndefinedVariable
                
                self.widgets.seekBar.set_text("00:00 / " + dur_str)                    
                
                gtk.gdk.threads_leave() #@UndefinedVariable
                break
            except:
                print "Error"
                pass
                
        time.sleep(0.5)
        start_time = str(int(time.time()));
        
                    
        while play_thread_id == self.playerThreadId:
            pos_int = 0
            try:
                pos_int = self.player.query_position(self.time_format, None)[0]
            except gst.QueryError: 
                print "QueryError error..."
            
            pos_str = convert_ns(pos_int)
            if play_thread_id == self.playerThreadId:
                gtk.gdk.threads_enter() #@UndefinedVariable                   
                
                timeStr = pos_str + " / " + dur_str
                timePersent = (pos_int + 0.0) / dur_int
                
                              
                self.widgets.seekBar.set_text(timeStr)
                self.widgets.seekBar.set_fraction(timePersent)
                
                gtk.gdk.threads_leave() #@UndefinedVariable
                
                """report now playing song"""
                if song.getArtist() and song.getTitle():
                    scrobler.report_now_playing(song.getArtist(), song.getTitle())                
                
            time.sleep(1)            
            
            "Download only if you listen this music"
            if flag and song.type == CommonBean.TYPE_MUSIC_URL and timePersent > 0.35:
                flag = False                
                dowload_song_thread(song)
            
            if  self._get_state() != gst.STATE_PAUSED:
                sec += 1            
                #LOG.debug("Song duration", sec, timePersent);    
                            
            if not is_scrobled and (sec >= duration_sec / 2 or (sec >= 45 and timePersent >= 0.9)):
                is_scrobled = True   
                if song.getArtist() and song.getTitle():             
                    scrobler.scrobble(song.getArtist(), song.getTitle(), start_time, "P", "", duration_sec)
                    LOG.debug("Song Successfully scrobbled", song.getArtist(), song.getTitle())
                
    
    
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
            self.playerThreadId = None
            self.player = None            
            """Try to play next"""
                              
            
            
    
