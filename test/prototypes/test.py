import pygtk
pyGtk.require('2.0')
from gi.repository import Gtk

class Winder( Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

        box = Gtk.HBox()
        self.add(box)

        model = Gtk.TreeStore(str)
        tree = Gtk.TreeView(model)
        box.pack_start(tree)

        cell = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn('woot', cell, text=0)
        tree.append_column(col)

        #tree.enable_model_drag_dest([("text/uri-list", 0, 0)], Gtk.gdk.ACTION_COPY | Gtk.gdk.ACTION_MOVE) #@UndefinedVariable
        
    

        targets = [('text/uri-list', 0, 0)]
        
        tree.drag_source_set(Gtk.gdk.BUTTON1_MASK, targets,Gtk.gdk.ACTION_COPY|Gtk.gdk.ACTION_MOVE)
        #tree.enable_model_drag_source(Gtk.gdk.BUTTON1_MASK, [("text/uri-list", 0, 0)], Gtk.gdk.ACTION_COPY | Gtk.gdk.ACTION_MOVE) #@UndefinedVariable
        #tree.enable_model_drag_source(Gtk.gdk.BUTTON1_MASK, [('text/uri-list', 0, 0)], Gtk.gdk.ACTION_COPY | Gtk.gdk.ACTION_MOVE) #@UndefinedVariable
        tree.enable_model_drag_dest(targets, Gtk.gdk.ACTION_COPY|Gtk.gdk.ACTION_MOVE)
        
        tree.drag_source_set_icon_stock('gtk-dnd-multiple')

        for i in range(0, 100):
            model.append(None,['test_%d' % i])

        self.set_size_request(500, 500)
        self.show_all()

Winder()
Gtk.main()