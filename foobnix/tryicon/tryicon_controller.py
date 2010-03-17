'''
Created on Mar 13, 2010

@author: ivan
'''
import gtk
class TrayIcon:
    def __init__(self, gxTryIcon, windowController, playerController):
        self.windowController = windowController
        self.playerController = playerController        
        self.icon = gtk.StatusIcon()
        self.icon.set_tooltip("Foobnix music playerEngine")
        self.icon.set_from_stock("gtk-media-play")
        
        self.connect()       
        
        self.popup = gxTryIcon.get_widget("popUpWindow")
         
        signalsPopup = {
                "on_close_clicked" :self.quitApp,
                "on_play_clicked" :self.onPlayButton,
                "on_pause_clicked" :self.onPauseButton,
                "on_next_clicked" :self.onPlayNextButton,
                "on_prev_clicked" :self.onPlayPrevButton,
                "on_cancel_clicked": self.closePopUP
        }
        
        gxTryIcon.signal_autoconnect(signalsPopup)        
        self.isVisible = True
        
    def connect(self):
        self.icon.connect("activate", self.onLeftMouseClick)
        self.icon.connect("popup-menu", self.onRightMouseClick)
        
        #self.icon.connect("scroll-event", self.onScrollUpDown)
     
    def quitApp(self, *a):
        self.windowController.onDestroy()  
    
    def onPlayButton(self, *a):
        self.playerController.playState()
    
    def onPauseButton(self, *a):
        self.playerController.pauseState() 
        
    def onPlayNextButton(self, *a):
        self.playerController.next()
    
    def onPlayPrevButton(self, *a):
        self.playerController.prev() 
    
    def closePopUP(self, *a):
        self.popup.hide()
    
    
    def onLeftMouseClick(self, *a):         
        if self.isVisible:
            self.windowController.hide()                
        else:
            self.windowController.show()
        self.isVisible = not self.isVisible
    
    def onRightMouseClick(self, *args):      
        self.popup.show()
    
    def onScrollUpDown(self, *args):      
        pass
