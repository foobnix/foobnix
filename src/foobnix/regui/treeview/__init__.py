import gtk
import gobject
from deluge.log import LOG

class FModel():
    def __init__(self):        
        self.text = 0
        self.visible = 1
        self.font = 2
        self.play_icon = 3
        self.time = 4
        self.path = 5

class TreeViewControl(gtk.TreeView, FModel):
    
    def __init__(self):
        gtk.TreeView.__init__(self)   
        FModel.__init__(self)
             
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.set_enable_tree_lines(True)
        
        """model config"""
        self.model = gtk.TreeStore(str, gobject.TYPE_BOOLEAN, str, str, str)
        
        """filter config"""
        filter = self.model.filter_new()
        filter.set_visible_column(self.visible)
        self.set_model(filter)    
    
    def append(self, level=None, text=None, visible=True, font="normal", play_icon=None, time=None):        
        return self.model.append(level, [text, visible, font, play_icon, time])
   
    def clear(self):
        self.model.clear() 
    
    def filter(self, query):
        LOG.info("Filter", query)
        if not query:
            """show alll"""
            for line in self.model:                
                line[self.visible] = True
                for child in line.iterchildren():
                    child[self.visible] = True
            self.collapse_all()
            return True

        """filter selected"""        
        query = query.lower()       
        for line in self.model:
            name = line[self.text].lower()

            if name.find(query) >= 0:
                LOG.info("FILTER FIND PARENT:", name, query)
                line[self.visible] = True
                self.expand_all()                    
            else:
                line[self.visible] = False
