'''
Created on Mar 16, 2010

@author: ivan
'''
'''
Created on Mar 11, 2010

@author: ivan
'''
import gtk
from foobnix.model.entity import CommonBean
class OnlineListModel:
    POS_ICON = 0
    POS_TRACK_NUMBER = 1
    POS_NAME = 2
    POS_PATH = 3
    POS_COLOR = 4
    POS_INDEX = 5
    POS_TYPE = 6
    POS_PARENT = 7
    
    def __init__(self, widget):
        self.widget = widget
        self.model = gtk.ListStore(str, str, str, str, str, int, str, str)
               
        cellpb = gtk.CellRendererPixbuf()
        cellpb.set_property('cell-background', 'yellow')
        iconColumn = gtk.TreeViewColumn('Icon', cellpb, stock_id=0, cell_background=4)
        numbetColumn = gtk.TreeViewColumn('N', gtk.CellRendererText(), text=1, background=4)
        descriptionColumn = gtk.TreeViewColumn('PlayList', gtk.CellRendererText(), text=2, background=4)
                
        widget.append_column(iconColumn)
        widget.append_column(numbetColumn)
        widget.append_column(descriptionColumn)
        
        widget.set_model(self.model)
    def getSize(self):
        return len(self.model)
    
    def getBeenByPosition(self, position):
        bean = CommonBean()
        bean.icon = self.model[position][ self.POS_ICON]
        bean.tracknumber = self.model[position][ self.POS_TRACK_NUMBER]
        bean.name = self.model[position][ self.POS_NAME]
        bean.path = self.model[position][ self.POS_PATH]
        bean.color = self.model[position][ self.POS_COLOR]
        bean.index = self.model[position][ self.POS_INDEX]
        bean.type = self.model[position][ self.POS_TYPE]
        bean.parent = self.model[position][ self.POS_PARENT]
        return bean  
    
    def getModel(self):
        return self.model

    def getSelectedBean(self):
        print self.widget
        selection = self.widget.get_selection()
        print selection
        model, selected = selection.get_selected()
        print model, selected
        if selected:
            bean = CommonBean()
            bean.icon = model.get_value(selected, self.POS_ICON)
            bean.tracknumber = model.get_value(selected, self.POS_TRACK_NUMBER)
            bean.name = model.get_value(selected, self.POS_NAME)
            bean.path = model.get_value(selected, self.POS_PATH)
            bean.color = model.get_value(selected, self.POS_COLOR)
            bean.index = model.get_value(selected, self.POS_INDEX)
            bean.type = model.get_value(selected, self.POS_TYPE)
            bean.parent = model.get_value(selected, self.POS_PARENT)
            return bean                
    
    def clear(self):
        self.model.clear()
    
    def append(self, bean):   
        print bean
        self.model.append([bean.icon, bean.tracknumber, bean.name, bean.path, bean.color, bean.index, bean.type, bean.parent])

    def __del__(self, *a):
        print "del"
