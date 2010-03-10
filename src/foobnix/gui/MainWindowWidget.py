from foobnix.gui.InitGlade import InitGlade
import gtk
from foobnix.util import LOG

class MainWindowWidget(InitGlade):
    def __init__(self, busController):
        InitGlade.__init__(self)
        self._mainWindowGlade = self.getTopLevel("foobnixWindow")
                
        WindowWiget(self._mainWindowGlade, busController)
        SeekProgressBar(self._mainWindowGlade, busController)
        
    def getGlade(self):
        return self._mainWindowGlade
    
class DirectoryWidget():
    def __init__(self, busControlle):        
        glade = InitGlade().getTopLevel("foobnixWindow")        
        self._window = glade.get_widget("direcotry_treeview")

class WindowWiget():
    def __init__(self,busController):
        glade = InitGlade().getTopLevel("foobnixWindow")        
        self._window = glade.get_widget("foobnixWindow")
        self._window.connect("destroy", self.exitFoobNIX)
                
    def exitFoobNIX(self, *event):
        LOG.info("Exit Button pressed", event)        
        gtk.main_quit()
        
    def show(self):
        self._window.show()
        
        
class SeekProgressBar():
    def __init__(self, busController):
        glade = InitGlade().getTopLevel("foobnixWindow")
        self._busController = busController
        self._seekBarWidget = glade.get_widget("seek_progressbar")
        self._seekEventBoxWidget = glade.get_widget("seek_eventbox") 
        self._seekEventBoxWidget.connect("button_press_event", self.onSeekChange)
        
    def onSeekChange(self, widget, event):            
        if event.button == 1:
            LOG.info("Seek Change")
            width = self._seekEventBoxWidget.allocation.width          
            x = event.x
            self._busController.setSeek((x + 0.0) / width * 100)            