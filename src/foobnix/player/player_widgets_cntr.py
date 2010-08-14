# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2010

@author: ivan
'''
from foobnix.lyric.lyr import get_lyrics
import thread
from foobnix.util import LOG
from foobnix.util.configuration import FConfiguration
from foobnix.online.google.translate import translate
from foobnix.util.mouse_utils import is_double_click
import time


class PlayerWidgetsCntl():
    '''
   
    '''
    def __init__(self, gxMain, playerCntr):
        self.playerCntr = playerCntr
        
        self.volume = gxMain.get_widget("volume_hscale")
        self.volume.connect("change-value", self.onVolumeChange)
        
        self.seek = gxMain.get_widget("seek_eventbox")
        self.seek.connect("button-press-event", self.onSeek)
        
        self.seekBar = gxMain.get_widget("seek_progressbar")
        self.timeLabel = gxMain.get_widget("seek_progressbar")
        
        self.vpanel = gxMain.get_widget("vpaned1")
        self.hpanel = gxMain.get_widget("hpaned1")
        #self.hpanel.connect("button-press-event", self.on_show_hide_paned);
        
        #self.hpanel.set_property("position-set", True)
        
        #self.hpanel2 = gxMain.get_widget("vpaned1")
        #print "POSITION", self.hpanel2.get_position()
        
        
        #self.lyric = gxMain.get_widget("lyric_textview")
        #self.textbuffer = self.lyric.get_buffer()
        
        #self.tr_lyric = gxMain.get_widget("translate_lyric_textview")
        #self.tr_textbuffer = self.tr_lyric.get_buffer()
        
        spinbutton1_tabs = gxMain.get_widget("spinbutton1_tabs")
        spinbutton1_tabs.set_value(FConfiguration().count_of_tabs)
        spinbutton1_tabs.connect("value-changed", self.on_chage_tabs)
                                                                     
        self.info_panel = gxMain.get_widget("info_frame")
        self.search_panel = gxMain.get_widget("search_frame")
        
        self.view_tree_panel = gxMain.get_widget("view-left-navigation")
        self.view_tree_panel.connect("toggled", self.show_tree_panel)
        
        self.view_info_panel = gxMain.get_widget("view-info-panel")
        self.view_info_panel.connect("toggled", self.show_info_panel)
        
        self.view_search_panel = gxMain.get_widget("view-search-panel")
        self.view_search_panel.connect("toggled", self.show_search_panel)
        
        self.statusbar = gxMain.get_widget("statusbar")
        
        navigationEvents = {                
                "on_play_button_clicked" :self.onPlayButton,
                "on_stop_button_clicked" :self.onStopButton,
                "on_pause_button_clicked" :self.onPauseButton,
                "on_prev_button_clicked" :self.onPrevButton,
                "on_next_button_clicked": self.onNextButton,
                
        }
        
        gxMain.signal_autoconnect(navigationEvents)
        
        self.show_info_panel(None, FConfiguration().view_info_panel)
        self.show_search_panel(None, FConfiguration().view_search_panel)
        self.show_tree_panel(None, FConfiguration().view_tree_panel)
    
    def show_info_panel(self, w, flag=True):
        if w:
            flag = w.get_active()
        if flag:
            self.info_panel.show()
        else:
            self.info_panel.hide()
        FConfiguration().view_info_panel = flag
        self.view_info_panel.set_active(flag)
    
    def show_search_panel(self, w, flag=True):
        if w:
            flag = w.get_active()            
        if flag:
            self.search_panel.show()
        else:
            self.search_panel.hide()
        FConfiguration().view_search_panel = flag
        self.view_search_panel.set_active(flag)    

    def show_tree_panel(self, w, flag=True):
        if w:
            flag = w.get_active()
        if flag:
            self.hpanel.set_position(FConfiguration().hpanelPostition)
        else:
            self.hpanel.set_position(0)
        FConfiguration().view_tree_panel = flag
        self.view_tree_panel.set_active(flag)
   
    def on_chage_tabs(self, w):
        val = w.get_value_as_int()
        FConfiguration().count_of_tabs = val
        LOG.debug("Set size of tabs", val)
        
        
    def on_show_hide_paned(self, w, e):
        #TODO: Matik, could you view, this signal rise on any paned double click.
        if is_double_click(e):
            LOG.debug("double click", w)
            if w.get_position() == 0:
                self.on_full_view(w, e)         
            else:
                self.on_compact_view(w, e)
            time.sleep(0.2)
                   
                
                
                      
   
    def setStatusText(self, text):
        self.statusbar.push(0, text)
   
    def setLiric(self, song):
        pass
        #thread.start_new_thread(self._setLiricThread, (song,))
    
    def _setLiricThread(self, song):
        self.tr_textbuffer.set_text("")
        
        title = "" + song.getTitle()
        for extension in FConfiguration().supportTypes:
            if title.endswith(extension):
                title = title.replace(extension, "")
                break
                
        LOG.info("Get lirics for:", song.getArtist(), title)
        if song.getArtist() and  song.getTitle():
            try:
                text = get_lyrics(song.getArtist(), title)
            except:
                self.setStatusText(_("Connection lyrics error"))
                LOG.error("Connection lyrics error")
                return None
                
            if text:
                header = "*** " + song.getArtist() + " - " + title + " ***" 
                self.textbuffer.set_text(header + "\n" + text)
                                
                LOG.info("try to translate")
                text_tr = self.getTranstalted(text)
                self.tr_textbuffer.set_text("*** " + song.getArtist() + " - " + title + " ***\n" + text_tr)
            else: 
                self.textbuffer.set_text("Not Found lyrics for " + song.getArtist() + " - " + title + "\n")
    
    def getTranstalted(self, text):
        input = ""
        result = ""
        for line in text.rsplit("\n"):            
            line = line + "#";
            input += line
            
        res = translate(input, src="", to="ru")
        
        for line in res.rsplit("#"):
            result = result + line + "\n"
        return result
    
    def is_ascii(self, s):
        return all(ord(c) < 128 for c in s)    
    
    def onPlayButton(self, *a):
        self.playerCntr.playState()
    
    def onStopButton(self, *a):
        self.playerCntr.stopState()
        
    def onPauseButton(self, *a):
        self.playerCntr.pauseState()
        
    def onPrevButton(self, *a):
        self.playerCntr.prev()
    
    def onNextButton(self, *a):
        self.playerCntr.next()
        
    def onSeek(self, widget, event):
        if event.button == 1:
            width = self.seek.allocation.width          
            x = event.x
            seekValue = (x + 0.0) / width * 100
            LOG.info(seekValue)
            self.playerCntr.setSeek(seekValue);            
        
    def onVolumeChange(self, widget, obj3, volume):                      
        self.playerCntr.setVolume(volume / 100)
        
    pass # end of class
