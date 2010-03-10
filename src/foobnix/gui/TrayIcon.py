import gtk
from foobnix.util import LOG
class TrayIcon:
    def __init__(self, windowService):
        self._windowService = windowService
        self.icon = gtk.StatusIcon()
        self.icon.set_tooltip("Foobnix music playerEngine")
        self.icon.set_from_stock("gtk-media-play")
        
        self.connect()
        
        
    def connect(self):
        self.icon.connect("activate", self.onLeftMouseClick)
        self.icon.connect("popup-menu", self.onRightMouseClick)
        self.icon.connect("scroll-event", self.onScrollUpDown)
    
    def onLeftMouseClick(self, *args):         
        if self._windowService.isVisible():
            self._windowService.hide()                
        else:
            self._windowService.show()
            
        self._windowService.setVisible(not self._windowService.isVisible())
        LOG.info("Left mouse click on icon")         
    
    def onRightMouseClick(self, *args):
        LOG.info("Right mouse click on icon")
        pass
    
    def onScrollUpDown(self, *args):
        LOG.info("Scroll on icon")
        pass  
    
