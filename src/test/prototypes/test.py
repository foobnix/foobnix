import pygtk
pygtk.require('2.0')
import gtk

class Winder( gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)

        box = gtk.HBox()
        self.add(box)

        model = gtk.TreeStore(str)
        tree = gtk.TreeView(model)
        box.pack_start(tree)

        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn('woot', cell, text=0)
        tree.append_column(col)

        #tree.enable_model_drag_dest([("text/uri-list", 0, 0)], gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE) #@UndefinedVariable
        
    

        targets = [('text/uri-list', 0, 0)]
        
        tree.drag_source_set(gtk.gdk.BUTTON1_MASK, targets,gtk.gdk.ACTION_COPY|gtk.gdk.ACTION_MOVE)
        #tree.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("text/uri-list", 0, 0)], gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE) #@UndefinedVariable
        #tree.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [('text/uri-list', 0, 0)], gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE) #@UndefinedVariable
        tree.enable_model_drag_dest(targets, gtk.gdk.ACTION_COPY|gtk.gdk.ACTION_MOVE)
        
        tree.drag_source_set_icon_stock('gtk-dnd-multiple')

        for i in range(0, 100):
            model.append(None,['test_%d' % i])

        self.set_size_request(500, 500)
        self.show_all()

Winder()
gtk.main()