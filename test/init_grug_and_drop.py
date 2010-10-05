import gtk

class BaseTree(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)
        
        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example", 0, 0)], gtk.gdk.ACTION_COPY)
        self.enable_model_drag_dest([("example", 0, 0)], gtk.gdk.ACTION_COPY)
        
        self.connect("drag_data_received", self.onDragDataReceived)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Integer", renderer, text=0)
        self.append_column(column)
        column = gtk.TreeViewColumn("String", renderer, text=1)
        self.append_column(column)
    
    def iterCopy(self, from_model, from_iter,to_model, to_iter, pos):   

        row = [from_model.get_value(from_iter, 0),from_model.get_value(from_iter, 1)]
        
        if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            new_iter = to_model.prepend(to_iter, row)
        elif pos == gtk.TREE_VIEW_DROP_BEFORE:
            new_iter = to_model.insert_before(None, to_iter, row)
        elif pos == gtk.TREE_VIEW_DROP_AFTER:
            new_iter = to_model.insert_after(None, to_iter,row)
        
        if from_model.iter_has_child(from_iter):
            for i in range(0, from_model.iter_n_children(from_iter)):
                next_iter_to_copy = from_model.iter_nth_child(from_iter, i)
                self.iterCopy(from_model, next_iter_to_copy,to_model,  new_iter, gtk.TREE_VIEW_DROP_INTO_OR_BEFORE)
    
    def onDragDataReceived(self, treeview, drag_context, x, y, selection, info, eventtime):    
        to_path, to_pos = treeview.get_dest_row_at_pos(x, y)      
        to_model = treeview.get_model()
        to_iter = to_model.get_iter(to_path)
        
        from_model, from_iter = drag_context.get_source_widget().get_selection().get_selected()
        
        self.iterCopy(from_model, from_iter, to_model, to_iter, to_pos)
        drag_context.finish(True, True, eventtime)
        
        treeview.expand_to_path(to_path)


class TreeOne(BaseTree):
    def __init__(self):
        BaseTree.__init__(self)
        model = gtk.TreeStore(int, str)
        data = [[0,"zero"],[1,"one"],[2,"two"],[3,"three"],[4,"four"],[5,"five"],[6,"six"]]
        for item in data:
            row = [item[0], item[1]]
            iter = model.append(None, row)
        self.set_model(model)
        

class TreeTwo(BaseTree):
    def __init__(self):
        BaseTree.__init__(self)
        model = gtk.TreeStore(int, str)
        data = [[0,"zero"],[1,"one"],[2,"two"],[3,"three"],[4,"four"],[5,"five"],[6,"six"]]
        for item in data:
            row = [item[0]+10, "2"+item[1]]
            iter = model.append(None, row)
        self.set_model(model)

class TreeDNDExample:
    def __init__(self):
    
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", gtk.mainquit)
        window.set_default_size(250, 350)
        
        one = TreeOne()
        two = TreeTwo()
        
        hbox = gtk.HBox(False,0)
        
        hbox.pack_start(one)
        hbox.pack_start(two)
        

        window.add(hbox)
        
        window.show_all()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    TreeDNDExample()
    main()
