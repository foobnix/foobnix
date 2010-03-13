'''
Created on Mar 11, 2010

@author: ivan
'''

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
        
        
           
        navigationEvents = {                
                "on_play_button_clicked" :self.onPlayButton,
                "on_stop_button_clicked" :self.onStopButton,
                "on_pause_button_clicked" :self.onPauseButton,
                "on_prev_button_clicked" :self.onPrevButton,
                "on_next_button_clicked": self.onNextButton
        }
        
        gxMain.signal_autoconnect(navigationEvents)        
    
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