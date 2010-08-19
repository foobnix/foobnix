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
    if username != FConfiguration().lfm_user_default:        
        scrobler = lastfm.get_scrobbler("fbx", "1.0")
        LOG.debug("lastfm Scroblerr enable for user", username)
    else:
        LOG.debug("NO lastfm Scroblerr enable for user", username)
        scrobler = None
        
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
        self.erros = 0
        self.prev_title = ""
        
        self.prev_path = ""
        

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
        LOG.info("play song", song.name, song.getArtist(), song.getTitle())
        
        if song.path != self.prev_path:        
            self.stopState()
        
        if not song:
            LOG.info("NULL song can't playing")
            return
        
        LOG.info("Path before", song.path)
        #Try to set resource
       
        LOG.info("Path after", song.path)
        if song.path == None or song.path == "":
            self.count += 1
            LOG.info("SONG NOT FOUND", song.name)
            LOG.info("Count is", self.count)
            if self.count > 5:
                return
            return self.next()
        
        self.count = 0
        self.widgets.setLiric(song)
            
        LOG.info("Type", song.type)
       
        LOG.info("MODE", self.mode)
        LOG.info("Name", song.name)
        
        if  song.type == CommonBean.TYPE_MUSIC_FILE:
            if song.path != self.prev_path:
                self.prev_path = song.path
                self.player = self.playerLocal()
                uri = 'file://' + urllib.pathname2url(song.path)
                if os.name == 'nt':
                    uri = 'file:' + urllib.pathname2url(song.path)
                
                self.player.set_property("uri", uri)
                self.playerThreadId = thread.start_new_thread(self.playThread, (song,))
                
        elif song.type == CommonBean.TYPE_RADIO_URL:
            LOG.info("URL PLAYING", song.path)
            self.player = self.playerHTTP()    
            path = get_radio_source(song.path)                    
            self.player.set_property("uri", path)
            self.widgets.seekBar.set_text("Url Playing...")
        elif song.type == CommonBean.TYPE_MUSIC_URL:
            LOG.info("URL PLAYING", song.path)
            self.player = self.playerHTTP()                        
            self.player.set_property("uri", song.path)                        
            self.playerThreadId = thread.start_new_thread(self.playThread, (song,))
        else:
            self.widgets.seekBar.set_text("Error playing...")
            return

        self.playState()
        print "SONG START", song.start_at
        if song.start_at > 0:
            self.set_seek_sec(song.start_at)
        
        self.setVolume(self.volume)
        
        
        self.onlineCntr.info.show_song_info(song)
        
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
        
        self.playerThreadId = None
        try:
            self.player.set_state(gst.STATE_NULL)
        except:
            pass
        self.player = None
        time.sleep(2)
        
        self.playbin = gst.element_factory_make("playbin", "player")  
        bus = self.playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.onBusMessage)     
        return self.playbin

    def playerLocal(self):
        LOG.info("Player Local Files")
        
        self.playerThreadId = None
        try:
            self.player.set_state(gst.STATE_NULL)
        except:
            pass
        self.player = None
        time.sleep(2)
        
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
        if self.player:
            return self.player.get_state()[1]
        else:
            return None
    
    def setSeek(self, persentValue):  
        if self._isStatusNull():
            self.playerThreadId = None
            return None
        pos_max = 1
        try:
            pos_max = self.player.query_duration(self.time_format, None)[0]
        except:
            LOG.error("Seek for new position error")

        if self.song and self.song.duration > 0:
            pos_max = int(self.song.duration) * 1000000000    
            
        seek_ns = pos_max * persentValue / 100;
        
        if self.song and self.song.duration > 0:
            seek_ns = seek_ns + int(self.song.start_at) * 1000000000
            
        LOG.info("SEC SEEK persent", seek_ns)  
        self.player.seek_simple(self.time_format, gst.SEEK_FLAG_FLUSH, seek_ns)
    
    def set_seek_sec(self, sec):  
        if self._isStatusNull():
            self.playerThreadId = None
            return None
        
        seek_ns = int(sec) * 1000000000 ;
        LOG.info("SEC SEEK SEC", seek_ns)  
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
                song = self.song
                LOG.info("Try")
                time.sleep(0.2)
                dur_int = self.player.query_duration(self.time_format, None)[0]
                
                if song.duration > 0:
                    dur_int = int(song.duration) * 1000000000
                
                duration_sec = dur_int / 1000000000
                dur_str = convert_ns(dur_int)
                
                gtk.gdk.threads_enter() #@UndefinedVariable
                self.widgets.seekBar.set_text("00:00 / " + dur_str)                    
                gtk.gdk.threads_leave() #@UndefinedVariable
                break
            except:
                LOG.info("Error")
                pass
                
        time.sleep(0.5)
        start_time = str(int(time.time()));
                    
        while play_thread_id == self.playerThreadId:
            pos_int = 0
            try:
                song = self.song
                dur_int = self.player.query_duration(self.time_format, None)[0]
                
                if song.duration > 0:
                    dur_int = int(song.duration) * 1000000000
                
                duration_sec = dur_int / 1000000000                
                dur_str = convert_ns(dur_int)
                
                pos_int = self.player.query_position(self.time_format, None)[0]
            except gst.QueryError: 
                LOG.info("QueryError error...")
                
            if song.duration > 0:
                    pos_int = pos_int - int(song.start_at) * 1000000000
            
            pos_str = convert_ns(pos_int)
            
            if play_thread_id == self.playerThreadId:
                gtk.gdk.threads_enter() #@UndefinedVariable                   
                
                timeStr = pos_str + " / " + dur_str
                timePersent = (pos_int + 0.0) / (dur_int)                
                              
                self.widgets.seekBar.set_text(timeStr)
                self.widgets.seekBar.set_fraction(timePersent)
                
                gtk.gdk.threads_leave() #@UndefinedVariable
                
                if  self._get_state() != gst.STATE_PAUSED:
                    sec += 1            
               
                if song.duration > 0 and pos_int > (int(song.duration) - 2) * 1000000000:
                    self.next()
               
                time.sleep(1)
                #self.on_notify_components(sec, pos_int, flag, is_scrobled, duration_sec, timePersent, start_time)
                if sec % 10 == 0:
                    LOG.info("Now playing...", song.getArtist(), song.getTitle())
                    #thread.start_new_thread(self.on_notify_components, (sec, pos_int, flag, is_scrobled, duration_sec, timePersent, start_time,))
                    """report now playing song"""        
                    if song.getArtist() and song.getTitle():
                        self.erros = 0
                        
                    if scrobler:
                        thread.start_new_thread(self.last_fm_reporting_thread, (song,))
                        #scrobler.report_now_playing(song.getArtist(), song.getTitle())
                
                
                    "Download only if you listen this music"
                    if flag and song.type == CommonBean.TYPE_MUSIC_URL and timePersent > 0.35:
                        flag = False                            
                        dowload_song_thread(song)
                                    
                    if not is_scrobled and (sec >= duration_sec / 2 or (sec >= 45 and timePersent >= 0.9)):
                        is_scrobled = True   
                        if song.getArtist() and song.getTitle():
                            try:
                                if scrobler:             
                                    scrobler.scrobble(song.getArtist(), song.getTitle(), start_time, "P", "", duration_sec)
                                LOG.debug("Song Successfully scrobbled", song.getArtist(), song.getTitle())
                            except:
                                LOG.error("Error reporting scobling", song.getArtist(), song.getTitle())      
    
    
    def last_fm_reporting_thread(self, song):
        LOG.info("last.fm report now playing")
        try:
            scrobler.report_now_playing(song.getArtist(), song.getTitle())
        except:
            LOG.error("Error reporting now playing last.fm", song.getArtist(), song.getTitle())
    
    def onBusMessage(self, bus, message): 
        #LOG.info(message   
        """Show radio info"""
        
        type = message.type
            
        if self.song.type == CommonBean.TYPE_RADIO_URL and type == gst.MESSAGE_TAG  and message.parse_tag():
            try:
                LOG.info(message, message.structure)
                self.erros = 0
                title = message.structure['title']
                self.widgets.seekBar.set_text("Radio: " + title)
                LOG.info("show title!", title)               
                self.song.name = title
                self.song.artist = None
                self.song.title = None
                
                print self.prev_title, title
                if title and self.song.type == CommonBean.TYPE_RADIO_URL and self.prev_title != title:
                    self.prev_title = title
                    LOG.info("show info!", self.song.name)
                    self.onlineCntr.info.show_song_info(self.song)
                    LOG.info(self.player.get_state()[1])
            except:
                LOG.warn("Messege info error appear")
                pass
            
            
                    
                
            #LOG.info(message.parse_tag()['title']
            
        elif type == gst.MESSAGE_EOS:
            
            LOG.info("MESSAGE_EOS")
            self.stopState()
            self.playerThreadId = None
            self.next()
                        

        elif type == gst.MESSAGE_ERROR:
            LOG.info("MESSAGE_ERROR")
            
            err, debug = message.parse_error()
            LOG.info("Error: %s" % err, debug, err.domain, err.code)
            if message.structure:
                name = message.structure.get_name()
                LOG.info("Structure name:", name)
                # name == "missing-plugin" or
                
                #in all cases we break playing, retry only if it paused.  
                if err.code != 1:
                    self.widgets.seekBar.set_text(str(err))
                    self.playerThreadId = None
                    self.player.set_state(gst.STATE_NULL)
                    #self.player = None    
                    return None
            
            
            self.widgets.seekBar.set_text(str(err))
            if self.song.path != self.prev_path: 
                self.playerThreadId = None
                self.player.set_state(gst.STATE_NULL)
            #self.player = None    
            time.sleep(4) 
            self.player.set_state(gst.STATE_NULL)
            if self.song.type == CommonBean.TYPE_RADIO_URL and self.erros <= 1:
                LOG.error("Error Num", self.erros)
                self.erros = self.erros + 1;                
                self.playSong(self.song)       
            """Try to play next"""
        else:
            #LOG.info(message
            pass                   
            
            
    
