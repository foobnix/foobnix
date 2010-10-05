try:
    import pygtk; pygtk.require("2.0")
except:
    pass
import gtk

data = [[0,"zero"],[1,"one"],[2,"two"],[3,"three"],[4,"four"],[5,"five"],[6,"six"]]

class TreeDNDExample:

    def checkSanity(self, model, iter_to_copy, target_iter):
    
        path_of_iter_to_copy = model.get_path(iter_to_copy)
        path_of_target_iter = model.get_path(target_iter)
        if path_of_target_iter[0:len(path_of_iter_to_copy)] == path_of_iter_to_copy:
            return False
        else:
            return True
    
    def iterCopy(self, model, iter_to_copy, target_iter, pos):   

        row = [model.get_value(iter_to_copy, 0),model.get_value(iter_to_copy, 1)]
        
        if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            new_iter = model.prepend(target_iter, row)
        elif pos == gtk.TREE_VIEW_DROP_BEFORE:
            new_iter = model.insert_before(None, target_iter, row)
        elif pos == gtk.TREE_VIEW_DROP_AFTER:
            new_iter = model.insert_after(None, target_iter,row)
        
        if model.iter_has_child(iter_to_copy):
            for i in range(0, model.iter_n_children(iter_to_copy)):
                next_iter_to_copy = model.iter_nth_child(iter_to_copy, i)
                self.iterCopy(model, next_iter_to_copy, new_iter, gtk.TREE_VIEW_DROP_INTO_OR_BEFORE)
    
    def onDragDataReceived(self, treeview, drag_context, x, y, selection, info, eventtime):    
        path, pos = treeview.get_dest_row_at_pos(x, y)      
        
        model, iter_to_copy = treeview.get_selection().get_selected()
        target_iter = model.get_iter(path)
        
        
        self.iterCopy(model, iter_to_copy, target_iter, pos)
        drag_context.finish(True, True, eventtime)
        
        treeview.expand_to_path(path)
      
    
    def __init__(self):
    
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", gtk.mainquit)
        window.set_default_size(250, 350)
        
        scrolledwin = gtk.ScrolledWindow()
        scrolledwin.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        window.add(scrolledwin)
        
        model = gtk.TreeStore(int, str)
        for item in data:
            iter = model.append(None)
            model.set(iter, 0, item[0], 1, item[1])
        
        treeview = gtk.TreeView(model)
        scrolledwin.add(treeview)
        
        treeview.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example", 0, 0)], gtk.gdk.ACTION_COPY)
        treeview.enable_model_drag_dest([("example", 0, 0)], gtk.gdk.ACTION_COPY)
        
        treeview.connect("drag_data_received", self.onDragDataReceived)
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Integer", renderer, text=0)
        treeview.append_column(column)
        column = gtk.TreeViewColumn("String", renderer, text=1)
        treeview.append_column(column)
        
        window.show_all()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
    TreeDNDExample()
    main()
