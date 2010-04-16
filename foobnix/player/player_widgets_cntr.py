# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2010

@author: ivan
'''
from foobnix.lyric.lyr import get_lyrics
import thread
import gtk
from foobnix.util import LOG
from foobnix.util.confguration import FConfiguration
from foobnix.online.google.translate import translate


class PlayerWidgetsCntl():
    '''
   
    '''
    def __init__(self, gxMain, playerCntr):
        self.playerCntr = playerCntr
        
        self.volume = gxMain.get_widget("volume_hscale")
        self.volume.connect("change-value",self.onVolumeChange)
        
        self.seek = gxMain.get_widget("seek_eventbox")
        self.seek.connect("button-press-event",self.onSeek)
        
        self.seekBar = gxMain.get_widget("seek_progressbar")
        self.timeLabel =  gxMain.get_widget("seek_progressbar")
        
        self.vpanel = gxMain.get_widget("vpaned1")
        self.hpanel = gxMain.get_widget("hpaned1")
        self.hpanel2 = gxMain.get_widget("hpaned2")
        
        
        self.lyric = gxMain.get_widget("lyric_textview")
        self.textbuffer = self.lyric.get_buffer()
        
        self.tr_lyric = gxMain.get_widget("translate_lyric_textview")
        self.tr_textbuffer = self.tr_lyric.get_buffer()
        
        
        
        self.statusbar = gxMain.get_widget("statusbar")
       
        self.lyric.set_editable(False)
        
        navigationEvents = {                
                "on_play_button_clicked" :self.onPlayButton,
                "on_stop_button_clicked" :self.onStopButton,
                "on_pause_button_clicked" :self.onPauseButton,
                "on_prev_button_clicked" :self.onPrevButton,
                "on_next_button_clicked": self.onNextButton
        }
        
        gxMain.signal_autoconnect(navigationEvents)        
        
   
    def setStatusText(self, text):
        self.statusbar.push(0,text)
   
    def setLiric(self, song):
        thread.start_new_thread(self._setLiricThread, (song,))
    
    def _setLiricThread(self, song):
        self.tr_textbuffer.set_text("")
        
        title = ""+song.getTitle()
        for extension in FConfiguration().supportTypes:
            if title.endswith(extension):
                title = title.replace(extension,"")
                break
                
        print "Get lirics for:", song.getArtist(),  title
        if song.getArtist() and  song.getTitle():
            try:
                text =  get_lyrics(song.getArtist(), title)
            except:
                self.setStatusText(_("Connection lyrics error"))
                LOG.error("Connection lyrics error")
                return None
                
            if text:
                header = "*** "+ song.getArtist() +" - " +title +" ***" 
                self.textbuffer.set_text(header+ "\n" +text)
                                
                LOG.info("try to translate")
                text_tr = self.getTranstalted(text)
                self.tr_textbuffer.set_text("*** "+ song.getArtist() +" - " +title +" ***\n" +text_tr)
            else: 
                self.textbuffer.set_text("Not Found lyrics for "+song.getArtist() +" - "+  title + "\n")
    
    def getTranstalted(self, text):
        input = ""
        result = ""
        for line in text.rsplit("\n"):            
            line = line + "#";
            input+=line
            
        res = translate(input, src="", to="ru")
        
        for line in res.rsplit("#"):
            result =result+ line + "\n"
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
            print seekValue
            self.playerCntr.setSeek(seekValue);            
        
    def onVolumeChange(self, widget, obj3, volume):                      
        self.playerCntr.setVolume(volume / 100)
        
    pass # end of class