import gtk


class RadioList:
    def __init__(self, widget):
        self.playListModel = gtk.ListStore(str)
        
        cellpb = gtk.CellRendererPixbuf()
        cellpb.set_property('cell-background', 'yellow')
        iconColumn = gtk.TreeViewColumn('Icon', cellpb, stock_id=0, cell_background=4)
        numbetColumn = gtk.TreeViewColumn('Radio Name', gtk.CellRendererText(), text=1, background=4)
        descriptionColumn = gtk.TreeViewColumn('Ratio Url', gtk.CellRendererText(), text=2, background=4)
                
        widget.append_column(iconColumn)
        widget.append_column(numbetColumn)
        widget.append_column(descriptionColumn)
        
        widget.set_model(self.playListModel)