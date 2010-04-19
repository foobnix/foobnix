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
        self.similar_songs_model = gtk.ListStore(str, str, str, str, str, int, str, str)
               
        cellpb = gtk.CellRendererPixbuf()
        cellpb.set_property('cell-background', 'yellow')
        iconColumn = gtk.TreeViewColumn(_('Icon'), cellpb, stock_id=0, cell_background=4)
        numbetColumn = gtk.TreeViewColumn(_('N'), gtk.CellRendererText(), text=1, background=4)
        descriptionColumn = gtk.TreeViewColumn(_('Music List'), gtk.CellRendererText(), text=2, background=4)
                
        widget.append_column(iconColumn)
        widget.append_column(numbetColumn)
        widget.append_column(descriptionColumn)
        
        widget.set_model(self.similar_songs_model)
    def getSize(self):
        return len(self.similar_songs_model)
    
    def getBeenByPosition(self, position):
        bean = CommonBean()
        bean.icon = self.similar_songs_model[position][ self.POS_ICON]
        bean.tracknumber = self.similar_songs_model[position][ self.POS_TRACK_NUMBER]
        bean.name = self.similar_songs_model[position][ self.POS_NAME]
        bean.path = self.similar_songs_model[position][ self.POS_PATH]
        bean.color = self.similar_songs_model[position][ self.POS_COLOR]
        bean.index = self.similar_songs_model[position][ self.POS_INDEX]
        bean.type = self.similar_songs_model[position][ self.POS_TYPE]
        bean.parent = self.similar_songs_model[position][ self.POS_PARENT]
        return bean  
    
    def getModel(self):
        return self.similar_songs_model

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
        self.similar_songs_model.clear()
    
    def append(self, bean):   
        print bean
        self.similar_songs_model.append([bean.icon, bean.tracknumber, bean.name, bean.path, bean.color, bean.index, bean.type, bean.parent])

    def __del__(self, *a):
        print "del"
