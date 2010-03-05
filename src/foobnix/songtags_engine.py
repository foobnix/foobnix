'''
Created on Feb 28, 2010

@author: ivan
'''
import gtk
class SongTagsEngine():
    def __init__(self, widget):
        self.widgetModel = gtk.ListStore(str, str,)
        
        nameColumn = gtk.TreeViewColumn('Name', gtk.CellRendererText(), text=0)
        valueColumn = gtk.TreeViewColumn('Value', gtk.CellRendererText(), text=1)
        
        widget.append_column(nameColumn)
        widget.append_column(valueColumn)
        
        widget.set_model(self.widgetModel)  
      
    def populate(self, song):
        self.widgetModel.clear()
        if song:
            print song.artist
            self.widgetModel.append(["Artist Name " , song.artist])
            self.widgetModel.append(["Track Title " , song.title])
            self.widgetModel.append(["Album Title " , song.album])
            self.widgetModel.append(["Date " , song.date])
            self.widgetModel.append(["Genre " , song.genre])
            self.widgetModel.append(["Track Number " , song.tracknumber])
            self.widgetModel.append(["File Name " , song.name])
            self.widgetModel.append(["File Path " , song.path])       
        
        
