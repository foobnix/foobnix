'''
Created on Mar 13, 2010

@author: ivan
'''
import gtk
import os.path
class TrayIcon:
    def __init__(self, gxTryIcon, windowController, playerController, playerWidgets):
        self.windowController = windowController
        self.playerController = playerController
        self.playerWidgets = playerWidgets        
        self.icon = gtk.StatusIcon()
        self.icon.set_tooltip("Foobnix music playerEngine")
        iconPath = "/usr/local/share/pixmaps/foobnix.png"
        if os.path.exists(iconPath):
            self.icon.set_from_file(iconPath)
        else:
            self.icon.set_from_stock("gtk-media-play")
        
        
        self.connect()       
        
        self.popup = gxTryIcon.get_widget("popUpWindow")
        self.text1 = gxTryIcon.get_widget("text1")
        self.text2 = gxTryIcon.get_widget("text2")
         
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
        try:
            self.icon.connect("scroll-event", self.onScrollUpDown)
        except:
            pass
    
    def setText1(self, text):
        self.text1.set_text(text) 
    
    def setText2(self, text):
        self.text2.set_text(text)
     
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
    
    def onScrollUpDown(self, w, event):      
        volume = self.playerController.getVolume()            
        if event.direction == gtk.gdk.SCROLL_UP: #@UndefinedVariable
            print "Volume UP"
            self.playerController.setVolume(volume + 0.05)                
        else:
            print "Volume Down"
            self.playerController.setVolume(volume - 0.05)
        
        self.playerWidgets.volume.set_value(volume * 100)  
