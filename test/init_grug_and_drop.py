import gtk
import gobject

class BaseTree(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)
        column = gtk.TreeViewColumn("id", gtk.CellRendererText(), text=0)
        self.append_column(column)
        
        column = gtk.TreeViewColumn("value", gtk.CellRendererText(), text=1)
        self.append_column(column)
        
        model = gtk.TreeStore(int, str, gobject.TYPE_BOOLEAN)

        filter_model = model.filter_new()        
        filter_model.set_visible_column(2)
        self.set_model(filter_model)

        for i, item in enumerate(["zero", "one", "two", "three", "four", "five", "six"]):            
            model.append(None, [i, item, i % 2])
        
        
        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example", 0, 0)], gtk.gdk.ACTION_COPY)
        self.enable_model_drag_dest([("example", 0, 0)], gtk.gdk.ACTION_COPY)
        
        self.connect("drag_drop", self.on_drag_drop)
        
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        
    def iter_copy(self, from_model, from_iter, to_model, to_iter, pos):   

        row = [from_model.get_value(from_iter, 0), from_model.get_value(from_iter, 1), True]
        
        if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            new_iter = to_model.prepend(to_iter, row)
        elif pos == gtk.TREE_VIEW_DROP_BEFORE:
            new_iter = to_model.insert_before(None, to_iter, row)
        elif pos == gtk.TREE_VIEW_DROP_AFTER:
            new_iter = to_model.insert_after(None, to_iter, row)
        else:
            new_iter = to_model.append(None, row)
        
        if from_model.iter_has_child(from_iter):
            for i in range(0, from_model.iter_n_children(from_iter)):
                next_iter_to_copy = from_model.iter_nth_child(from_iter, i)
                self.iter_copy(from_model, next_iter_to_copy, to_model, new_iter, gtk.TREE_VIEW_DROP_INTO_OR_BEFORE)
    
    def on_drag_drop(self, to_tree, drag_context, x, y, selection):
        to_filter_model = to_tree.get_model()
        to_model = to_filter_model.get_model()
        if to_tree.get_dest_row_at_pos(x, y):
            to_path, to_pos = to_tree.get_dest_row_at_pos(x, y)
            to_path = to_filter_model.convert_path_to_child_path(to_path)      
            to_iter = to_model.get_iter(to_path)
        else:
            to_path = None
            to_pos = None     
            to_iter = None
            
        
        from_tree = drag_context.get_source_widget()
        from_filter_model, from_paths = from_tree.get_selection().get_selected_rows()
        from_model = from_filter_model.get_model()
        from_path = from_filter_model.convert_path_to_child_path(from_paths[0]) 
        from_iter = from_model.get_iter(from_path)
        
        self.iter_copy(from_model, from_iter, to_model, to_iter, to_pos)
        
        if to_tree == from_tree:
            """move element in the save tree"""
            drag_context.finish(True, True)
        
        if to_path:
            to_tree.expand_to_path(to_path)


class TreeOne(BaseTree):
    def __init__(self):
        BaseTree.__init__(self)

class TreeTwo(BaseTree):
    def __init__(self):
        BaseTree.__init__(self)

class TwoTreeExample:
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", gtk.main_quit)
        window.set_default_size(250, 350)
        
        one = TreeOne()
        two = TreeTwo()
        
        hbox = gtk.HBox(False, 0)
        
        hbox.pack_start(one)
        hbox.pack_start(two)

        window.add(hbox)
        window.show_all()

if __name__ == "__main__":
    TwoTreeExample()
    gtk.main()
