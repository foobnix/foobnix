#-*- coding: utf-8 -*-
'''
Created on 28 сент. 2010

@author: ivan
'''
import gst
import urllib
import os
from foobnix.regui.engine import MediaPlayerEngine
from foobnix.util import LOG
import time
import gtk
import thread

class GStreamerEngine(MediaPlayerEngine):
    def __init__(self, controls):
        MediaPlayerEngine.__init__(self, controls)        
        
        self.player = self.init_local()
        self.position_sec = 0
        self.duration_sec = 0
        
        self.prev_path = None
    
    def init_local(self):         
        playbin = gst.element_factory_make("playbin2", "player")
        bus = playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)    
        LOG.debug("LOCAL gstreamer")    
        return playbin
    
    def init_http(self):         
        playbin = gst.element_factory_make("playbin", "player")
        bus = playbin.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        LOG.debug("HTTP gstreamer")        
        return playbin       
    
    def notify_init(self, duraction_int):
        LOG.debug("Pre init thread", duraction_int)
    
    def notify_playing(self, position_int, duration_int):
        #LOG.debug("Notify playing", position_int)
        self.position_sec = position_int / 1000000000 
        self.duration_sec = duration_int / 1000000000 
        self.controls.notify_playing(self.position_sec, self.duration_sec)
    
    def notify_eos(self):
        LOG.debug("Notify eos")
        self.controls.notify_eos()
        
    
    def notify_error(self):
        LOG.debug("Notify error")
    
    def play(self, path, start_sec=0):     
        if not path:
            LOG.error("Can't play empty path!!!")
            return None   
        
        self.state_stop()
        
        if path.startswith("http://"):
            self.player = self.init_http()
            uri = path
        else:
            self.player = self.init_local()
            uri = 'file://' + urllib.pathname2url(path)
            if os.name == 'nt':
                uri = 'file:' + urllib.pathname2url(path)
        
        print path
        self.player.set_property("uri", uri)            
        self.state_play()    
        
        self.play_thread_id = thread.start_new_thread(self.playing_thread, (start_sec,))
            
    
    def playing_thread(self, start_sec):
        thread_id = self.play_thread_id
        error_count = 0
        
        while thread_id == self.play_thread_id:
            try:                
                time.sleep(0.2)
                duraction_int = self.player.query_duration(gst.Format(gst.FORMAT_TIME), None)[0]
                if duraction_int == -1:
                    continue
                gtk.gdk.threads_enter()                #@UndefinedVariable
                self.notify_init(duraction_int)
                gtk.gdk.threads_leave() #@UndefinedVariable
                break                                                      
            except Exception, e:
                LOG.info("Init playing thread", e)
                time.sleep(1)
                if error_count > 3:
                    LOG.warn("shit happens")
                    self.state_stop()
                    time.sleep(1)                                       
                    self.state_play()
                error_count +=1

        time.sleep(0.2)
                    
        while thread_id == self.play_thread_id:            
            try:               
                position_int = self.player.query_position(gst.Format(gst.FORMAT_TIME), None)[0]
                gtk.gdk.threads_enter() #@UndefinedVariable
                self.notify_playing(position_int, duraction_int)
                gtk.gdk.threads_leave()                #@UndefinedVariable
            except Exception, e: 
                LOG.info("Playing thread error...")
               
            time.sleep(1)    
    
    def seek(self, percent):
        seek_ns = self.duration_sec * percent / 100 * 1000000000;
        self.player.seek_simple(gst.Format(gst.FORMAT_TIME), gst.SEEK_FLAG_FLUSH, seek_ns)
    
    def seek_seconds(self, seconds):
        LOG.info("Start with seconds", seconds)
        seek_ns = (float(seconds)+0.123)  * 1000000000       
        LOG.info("SEC SEEK SEC", seek_ns)         
        self.player.seek_simple(gst.Format(gst.FORMAT_TIME), gst.SEEK_FLAG_FLUSH, seek_ns)
    
    def volume(self, percent):
        value = percent / 100.0
        LOG.info("Set volume", value)
        self.player.set_property('volume', value)
    
    def state_play(self):
        self.player.set_state(gst.STATE_PLAYING)
        
    def state_stop(self):
        self.play_thread_id = None
        self.player.set_state(gst.STATE_NULL)
        
    def state_pause(self):
        
        #self.player.set_state(gst.STATE_VOID_PENDING)
        self.player.set_state(gst.STATE_PAUSED)
    
    def on_message(self, bus, message):
        print bus, message
        type = message.type
        if type == gst.MESSAGE_EOS:            
            LOG.info("MESSAGE_EOS")            
            self.notify_eos()
        elif type == gst.MESSAGE_ERROR:
            LOG.info("MESSAGE_ERROR")
            self.notify_error()
