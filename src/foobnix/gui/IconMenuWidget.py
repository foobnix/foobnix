'''
Created on Mar 6, 2010

@author: ivan
'''
from foobnix.gui.InitGlade import InitGlade
class IconMenuWidget(InitGlade):
    def __init__(self, topLevelGlade):
        InitGlade.__init__(self)
        self.popUpGlade = InitGlade.getTopLevel("popUpWindow")
        
        signalsPopUp = {
                    "on_close_clicked" :self.quitApp,
                    "on_play_clicked" :self.onPlayButton,
                    "on_pause_clicked" :self.onPauseButton,
                    "on_next_clicked" :self.onPlayNextButton,
                    "on_prev_clicked" :self.onPlayPrevButton,
                    "on_cancel_clicked": self.closePopUP
            }
            
        self.popUpGlade.signal_autoconnect(signalsPopUp)
        self.menuPopUp = self.popUpGlade.get_widget("popUpWindow")
        
