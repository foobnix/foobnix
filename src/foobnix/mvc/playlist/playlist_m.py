'''
Created on Mar 11, 2010

@author: ivan
'''
import gtk
class PlaylistModel:
    POS_ICON = 0
    POS_TRACK_NUMBER = 1
    POS_DESCRIPTIOPN = 2
    POS_PATH = 3
    POS_COLOR = 4
    
    def __init__(self, widget):
        self.model = gtk.ListStore(str, str, str, str, str)
               
        cellpb = gtk.CellRendererPixbuf()
        cellpb.set_property('cell-background', 'yellow')
        iconColumn = gtk.TreeViewColumn('Icon', cellpb, stock_id=0, cell_background=4)
        numbetColumn = gtk.TreeViewColumn('N', gtk.CellRendererText(), text=1, background=4)
        descriptionColumn = gtk.TreeViewColumn('PlayList', gtk.CellRendererText(), text=2, background=4)
                
        widget.append_column(iconColumn)
        widget.append_column(numbetColumn)
        widget.append_column(descriptionColumn)
        
        widget.set_model(self.model)
        
    def append(self, bean):   
        self.model.append([bean.icon, bean.tracknumber, bean.description, bean.path, bean.color])
 
class PlaylistBean():
    
    def __init__(self, icon, tracknumber, description, path, color):
        self.icon = icon
        self.tracknumber = tracknumber
        self.description = description
        self.path = path
        self.color = color 