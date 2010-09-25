import gtk
import gobject
from deluge.log import LOG
class TreeViewControl(gtk.TreeView):
    i = -1
    POS_TEXT = 0
    POS_VISIBLE = 1
    POS_FONT = 2
    POS_PLAY_ICON = 3
    POS_TIME = 4
    
    def __init__(self):
        gtk.TreeView.__init__(self)        
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.set_enable_tree_lines(True)
        
        """model config"""
        self.model = gtk.TreeStore(str, gobject.TYPE_BOOLEAN, str, str, str)
        
        """filter config"""
        filter = self.model.filter_new()
        filter.set_visible_column(self.POS_VISIBLE)
        self.set_model(filter)    
    
    def append(self, level=None, POS_TEXT=None, POS_VISIBLE=True, POS_FONT="normal", POS_PLAY_ICON=None, POS_TIME=None):        
        return self.model.append(level, [POS_TEXT, POS_VISIBLE, POS_FONT, POS_PLAY_ICON, POS_TIME])
   
    def clear(self):
        self.model.clear() 
    
    def filter(self, query):
        LOG.info("Filter", query)
        if not query:
            """show alll"""
            for line in self.model:                
                line[self.POS_VISIBLE] = True
                for child in line.iterchildren():
                    child[self.POS_VISIBLE] = True
            self.collapse_all()
            return True

        """filter selected"""        
        query = query.lower()       
        for line in self.model:
            name = line[self.POS_TEXT].lower()

            if name.find(query) >= 0:
                LOG.info("FILTER FIND PARENT:", name, query)
                line[self.POS_VISIBLE] = True
                self.expand_all()                    
            else:
                line[self.POS_VISIBLE] = False
                    
    def populate_from_scanner(self, scanner_beans):
        self.model.clear()
        hash = {None:None}
        for bean in scanner_beans:
            if hash.has_key(bean.parent):
                level = hash[bean.parent]
            else:
                level = None

            if bean.is_file:
                child_level = self.append(level, bean.name, True, "normal")
            else:
                child_level = self.append(level, bean.name, True, "bold")
                
            hash[bean.path] = child_level
