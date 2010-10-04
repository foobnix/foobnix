'''
Created on Oct 4, 2010

@author: ivan
'''
#!/usr/bin/env python

try:
    import pygtk; pygtk.require("2.0")
except:
    pass
import gtk

data = [[0, "zero"], [1, "one"], [2, "two"], [3, "three"], [4, "four"], [5, "five"], [6, "six"]]
data1 = [[10, "1zero"], [11, "1one"], [12, "1two"], [13, "1three"], [14, "1four"], [15, "1five"], [16, "1six"]]

class CoreTree(gtk.ScrolledWindow):
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
       
        
        self.model = gtk.TreeStore(int, str)
        
        self.treeview = gtk.TreeView(self.model)
        self.treeview.connect("drag-drop", self.on_drag_drop)
        #self.treeview.connect("drag-data-received", self.on_drag_data_received)
        
        self.treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.add(self.treeview)
        
        self.treeview.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example", 0, 0)], gtk.gdk.ACTION_COPY)
        self.treeview.enable_model_drag_dest([("example", 0, 0)], gtk.gdk.ACTION_COPY)
        
        
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Integer", renderer, text=0)
        self.treeview.append_column(column)
        column = gtk.TreeViewColumn("String", renderer, text=1)
        self.treeview.append_column(column)
    
         
      
    def iter_copy(self, to_pos, to_model, to_iter, from_model, from_iter):
        data_column_0 = from_model.get_value(from_iter, 0)
        data_column_1 = from_model.get_value(from_iter, 1)
        
        if (to_pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (to_pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            print "to parrent"
            new_iter = to_model.prepend(to_iter, None)
        elif to_pos == gtk.TREE_VIEW_DROP_BEFORE:
            print "insert before"
            new_iter = to_model.insert_before(None, to_iter)
            pass
        elif to_pos == gtk.TREE_VIEW_DROP_AFTER:
            print "insert after"
            new_iter = to_model.insert_after(None, to_iter)
            pass
        
        
        print "TO", to_model.iter_is_valid(new_iter)
        print "FROM", from_model.iter_is_valid(new_iter)
        
        to_model.set_value(new_iter, 0, data_column_0)
        to_model.set_value(new_iter, 1, data_column_1)
        
        
        if from_model.iter_has_child(from_iter):
            for i in xrange(0, from_model.iter_n_children(from_iter)):
                next_from_iter = from_model.iter_nth_child(from_iter, i)
                self.iter_copy(gtk.TREE_VIEW_DROP_INTO_OR_BEFORE, to_model, new_iter, from_model, next_from_iter)
                
    
    def on_drag_drop(self, to_tree, drag_context, x, y, selection):
        print to_tree, drag_context, x, y, selection
     
        """from widget selected"""                
        from_tree = drag_context.get_source_widget()
        from_model, from_paths = from_tree.get_selection().get_selected_rows()
        from_iter = from_model.get_iter(from_paths[0])
        print "from model:", from_model.get_value(from_iter, 1)
        
        
        """to current """
        print to_tree, x, y        
        to_model = to_tree.get_model()
        if not to_tree.get_dest_row_at_pos(x, y):
            to_model.append(None, from_iter)
            return None
        
        to_path, to_pos = to_tree.get_dest_row_at_pos(x, y)
        #to_model, to_paths = to_tree.get_selection().get_selected_rows()
        to_model = to_tree.get_model()
        to_iter = to_model.get_iter(to_path)        
        print "to model:", to_model.get_value(to_iter, 1)   
        
        self.iter_copy(to_pos, to_model, to_iter, from_model, from_iter)        
        to_tree.expand_to_path(to_path)
        
                
        pass
        
    
class TreeOne(CoreTree):
    def __init__(self):
        CoreTree.__init__(self)
        for item in data:
            iter = self.model.append(None)
            self.model.set(iter, 0, item[0], 1, item[1])
    
   
class TreeTwo(CoreTree):
    def __init__(self):
        CoreTree.__init__(self)
        for item in data1:
            iter = self.model.append(None)
            self.model.set(iter, 0, item[0], 1, item[1])

class TreeDNDExample:

    def __init__(self):
    
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", gtk.main_quit)
        window.set_default_size(250, 350)
        
        hbox = gtk.HBox(False, 0)
        
        one = TreeOne()
        two = TreeTwo()
        
        
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
