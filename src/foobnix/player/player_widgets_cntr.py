# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2010

@author: ivan
'''
from foobnix.lyric.lyr import get_lyrics
from foobnix.util import LOG, const
from foobnix.util.configuration import FConfiguration, VERSION
from foobnix.online.google.translate import translate
from foobnix.util.mouse_utils import is_double_click
import time
from foobnix.preferences.preferences_window import PreferencesWindow
import gtk
import urllib2


class PlayerWidgetsCntl():
    '''
   
    '''
    
    def scroll_event(self, button, event):
        volume = self.volume.get_value()
        if event.direction == gtk.gdk.SCROLL_UP:
            self.volume.set_value(volume + 1)
        else:
            self.volume.set_value(volume - 1)
        
        self.playerCntr.setVolume(volume / 100)
        
        return True

    
    def __init__(self, gxMain, playerCntr):
        self.playerCntr = playerCntr
        self.gxMain = gxMain
        self.volume = gxMain.get_widget("volume_hscale")
        self.volume.connect("change-value", self.onVolumeChange)
        self.volume.connect("scroll-event", self.scroll_event)

        
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
        
                                                                     
        self.info_panel = gxMain.get_widget("info_frame")
        self.search_panel = gxMain.get_widget("search_frame")
        self.lyric_panel = gxMain.get_widget("lyric_frame")
        
        self.view_tree_panel = gxMain.get_widget("view-left-navigation")
        self.view_tree_panel.connect("toggled", self.show_tree_panel)
        
        self.view_info_panel = gxMain.get_widget("view-info-panel")
        self.view_info_panel.connect("toggled", self.show_info_panel)
        
        self.view_search_panel = gxMain.get_widget("view-search-panel")
        self.view_search_panel.connect("toggled", self.show_search_panel)
        
        self.view_lyric_panel = gxMain.get_widget("view-lyric-panel")
        self.view_lyric_panel.connect("toggled", self.show_lyric_panel)
        
        """playback menu"""
        self.set_update_menu_item("linea_menu", "play_ordering", const.ORDER_LINEAR)
        self.set_update_menu_item("random_menu", "play_ordering", const.ORDER_RANDOM)
        
        self.set_update_menu_item("loop_all_menu", "play_looping", const.LOPPING_LOOP_ALL)
        self.set_update_menu_item("loop_single_menu", "play_looping", const.LOPPING_SINGLE)
        self.set_update_menu_item("dont_loop_menu", "play_looping", const.LOPPING_DONT_LOOP)
        
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
        self.show_lyric_panel(None, FConfiguration().view_lyric_panel)
        
        self.check_version()
        
    def check_version(self):        
        uuid= FConfiguration().uuid
        current_version = VERSION
        print uuid 
        try:
            f = urllib2.urlopen("http://www.foobnix.com/version?uuid="+uuid)
        except:            
            return None
        
        new_version = f.read()
        f.close()
        if current_version < new_version:
            self.setStatusText(_("New version ")+new_version+_(" avaliable at www.foobnix.com"));
             
    
    def set_update_menu_item(self, menu_item, conf_constant, value):
        def set_value(a, b):
            if a == "play_looping":
                FConfiguration().play_looping = b
            elif a == "play_ordering":
                FConfiguration().play_ordering = b
            
        liner = self.gxMain.get_widget(menu_item)        
        liner.connect("toggled", lambda * a: set_value(conf_constant, value))
        
        if conf_constant == "play_ordering":
            if FConfiguration().play_ordering == value:                           
                liner.set_active(True)
        elif conf_constant == "play_looping":
            if FConfiguration().play_looping == value:                           
                liner.set_active(True)
        
             
    
    def show_info_panel(self, w, flag=True):
        if w:
            flag = w.get_active()
        if flag:
            self.lyric_panel.hide()
            FConfiguration().view_lyric_panel = False
            self.view_lyric_panel.set_active(False)    
            
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
        
    def show_lyric_panel(self, w, flag=True):
        if w:
            flag = w.get_active()            
        if flag:
            
            self.info_panel.hide()
            FConfiguration().view_info_panel = False
            self.view_info_panel.set_active(False)
            
            
            self.lyric_panel.show()
        else:
            self.lyric_panel.hide()
        FConfiguration().view_lyric_panel = flag
        self.view_lyric_panel.set_active(flag)        

    def show_tree_panel(self, w, flag=True):
        if w:
            flag = w.get_active()
        if flag:
            self.hpanel.set_position(FConfiguration().hpanelPostition)
        else:
            self.hpanel.set_position(0)
        FConfiguration().view_tree_panel = flag
        self.view_tree_panel.set_active(flag)
   
        
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
                header = " *** " + song.getArtist() + " - " + title + " *** " 
                self.textbuffer.set_text(header + "\n" + text)
                                
                LOG.info("try to translate")
                text_tr = self.getTranstalted(text)
                self.tr_textbuffer.set_text("*** " + song.getArtist() + " - " + title + " *** \n" + text_tr)
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
