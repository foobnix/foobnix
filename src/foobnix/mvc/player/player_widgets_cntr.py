'''
Created on Mar 11, 2010

@author: ivan
'''

class PlayerWidgetsCntl():
    '''
   
    '''
    def __init__(self, gx, playerCntr):
        self.playerCntr = playerCntr
        
        self.volume = gx.get_widget("volume_hscale")
        self.volume.connect("change-value",self.onVolumeChange)
        
        self.seek = gx.get_widget("seek_eventbox")
        self.seek.connect("button-press-event",self.onSeek)
        
        self.seekBar = gx.get_widget("seek_progressbar")
        
        
        pass
    
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