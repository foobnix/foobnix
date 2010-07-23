'''
Created on Mar 11, 2010

@author: ivan
'''
import gtk
from foobnix.model.entity import CommonBean
from foobnix.util import LOG
class PlaylistModel:
    POS_ICON = 0
    POS_TRACK_NUMBER = 1
    POS_NAME = 2
    POS_PATH = 3
    POS_COLOR = 4
    POS_INDEX = 5
    POS_TYPE = 6
    
    def __init__(self, widget):
        self.widget = widget
        self.current_list_model = gtk.ListStore(str, str, str, str, str, int, str)
               
        cellpb = gtk.CellRendererPixbuf()
        cellpb.set_property('cell-background', 'yellow')
        iconColumn = gtk.TreeViewColumn(_('Icon'), cellpb, stock_id=0, cell_background=4)
        numbetColumn = gtk.TreeViewColumn(_('N'), gtk.CellRendererText(), text=1, background=4)
        descriptionColumn = gtk.TreeViewColumn(_("Music List"), gtk.CellRendererText(), text=2, background=4)
                
        widget.append_column(iconColumn)
        widget.append_column(numbetColumn)
        widget.append_column(descriptionColumn)
        
        widget.set_model(self.current_list_model)
    
    def getBeenByPosition(self, position):
        if position >= len(self.current_list_model):
            LOG.error("Song index too much", position)
            return None
    
        bean = CommonBean() 
        bean.icon = self.current_list_model[position][ self.POS_ICON]
        bean.tracknumber = self.current_list_model[position][ self.POS_TRACK_NUMBER]
        bean.name = self.current_list_model[position][ self.POS_NAME]
        bean.path = self.current_list_model[position][ self.POS_PATH]
        bean.color = self.current_list_model[position][ self.POS_COLOR]
        bean.index = self.current_list_model[position][ self.POS_INDEX]
        bean.type = self.current_list_model[position][ self.POS_TYPE]
        return bean       

    def get_all_beans(self):
        beans = []
        for i in xrange(len(self.current_list_model)):
            beans.append(self.getBeenByPosition(i))
        return beans
    
    def set_all_beans(self, beans):
        self.clear()
        for bean in beans:
            self.append(bean)
    
    def append_all_beans(self, beans):        
        for bean in beans:
            self.append(bean)
        
    
    def getSelectedBean(self):
        selection = self.widget.get_selection()
        model, selected = selection.get_selected()
        
        if selected:
            bean = CommonBean() 
            bean.icon = model.get_value(selected, self.POS_ICON)
            bean.tracknumber = model.get_value(selected, self.POS_TRACK_NUMBER)
            bean.name = model.get_value(selected, self.POS_NAME)
            bean.path = model.get_value(selected, self.POS_PATH)
            bean.color = model.get_value(selected, self.POS_COLOR)
            bean.index = model.get_value(selected, self.POS_INDEX)
            bean.type = model.get_value(selected, self.POS_TYPE)
        return bean                       
    
    def clear(self):
        self.current_list_model.clear()
 
            
    def append(self, bean):   
        self.current_list_model.append([bean.icon, bean.tracknumber, bean.name, bean.path, bean.color, bean.index, bean.type])

    def __del__(self, *a):
        LOG.info("del")
