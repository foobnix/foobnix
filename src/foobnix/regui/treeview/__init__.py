import gtk
import gobject
from deluge.log import LOG
class TreeViewControl(gtk.TreeView):
    POS_TEXT = 0
    POS_VISIBLE = 1
    POS_FONT = 2
    
    def __init__(self, title):
        gtk.TreeView.__init__(self)
        
        """model config"""
        self.model = gtk.TreeStore(str, gobject.TYPE_BOOLEAN, str)
        renderer = gtk.CellRendererText()
        
        """column config"""
        column = gtk.TreeViewColumn(title, renderer, text=self.POS_TEXT, font=self.POS_FONT)
        column.set_resizable(True)
        self.append_column(column)

        """filter config"""
        filter = self.model.filter_new()
        filter.set_visible_column(self.POS_VISIBLE)
        self.set_model(filter)    
    
    def append(self, level=None, POS_TEXT="", POS_VISIBLE=True, POS_FONT="normal"):        
        return self.model.append(level, [POS_TEXT, POS_VISIBLE, POS_FONT])
   
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

            child_level = self.append(level, bean.name)
            hash[bean.path] = child_level
