'''
Created on Mar 16, 2010

@author: ivan
'''
'''
Created on Mar 11, 2010

@author: ivan
'''
import gtk
from foobnix.model.entity import PlaylistBean
class OnlineListModel:
    POS_ICON = 0
    POS_TRACK_NUMBER = 1
    POS_NAME = 2
    POS_PATH = 3
    POS_COLOR = 4
    POS_INDEX = 5
    POS_TYPE = 6
    
    def __init__(self, widget):
        self.widget = widget
        self.model = gtk.ListStore(str, str, str, str, str, int, str)
               
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
        
        icon = self.model[position][ self.POS_ICON]
        tracknumber = self.model[position][ self.POS_TRACK_NUMBER]
        name = self.model[position][ self.POS_NAME]
        path = self.model[position][ self.POS_PATH]
        color = self.model[position][ self.POS_COLOR]
        index = self.model[position][ self.POS_INDEX]
        type = self.model[position][ self.POS_TYPE]
        return PlaylistBean(icon, tracknumber, name, path, color, index,type)       

    def getSelectedBean(self):
        print self.widget
        selection = self.widget.get_selection()
        print selection
        model, selected = selection.get_selected()
        print model, selected
        if selected:
            icon = model.get_value(selected, self.POS_ICON)
            tracknumber = model.get_value(selected, self.POS_TRACK_NUMBER)
            name = model.get_value(selected, self.POS_NAME)
            path = model.get_value(selected, self.POS_PATH)
            color = model.get_value(selected, self.POS_COLOR)
            index = model.get_value(selected, self.POS_INDEX)
            type = model.get_value(selected, self.POS_TYPE)
            print icon
            return PlaylistBean(icon, tracknumber, name, path, color, index, type)                       
    
    def clear(self):
        self.model.clear()
 
            
    def append(self, playlistBean):   
        self.model.append([playlistBean.icon, playlistBean.tracknumber, playlistBean.name, playlistBean.path, playlistBean.color, playlistBean.index, playlistBean.type])

    def __del__(self, *a):
        print "del"
