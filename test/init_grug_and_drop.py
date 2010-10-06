import gtk
import gobject
import copy

POS_index = 0
POS_text = 1
POS_visible = 2
POS_font = 3
POS_level = 4
POS_parent = 5

class Bean():
    def __init__(self, row=None):
        self.index = None        
        self.text = None
        self.visible = None
        self.font = None

        self.level = None
        self.parent = None
        
        self.path = None
        
        if row:
            self.index = row[0]
            self.text = row[1]
            self.visible = row[2]
            self.font = row[3]
            self.level = row[4]
            self.parent = row[5]
            
    def get_row(self):
        return [self.index, self.text, self.visible, self.font, self.level, self.parent]

class BaseTree(gtk.TreeView):
    def __init__(self):
        gtk.TreeView.__init__(self)
        column = gtk.TreeViewColumn("value", gtk.CellRendererText(), text=1, font=3)
        self.append_column(column)
        self.model_types = int, str, gobject.TYPE_BOOLEAN, str, str, str
        model = gtk.TreeStore(*self.model_types)

        filter_model = model.filter_new()        
        filter_model.set_visible_column(2)
        self.set_model(filter_model)

        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example", 0, 0)], gtk.gdk.ACTION_COPY)
        self.enable_model_drag_dest([("example", 0, 0)], gtk.gdk.ACTION_COPY)
        
        self.connect("drag_drop", self.on_drag_drop)
        
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        
        self.init_populate()
        
    def check_sanity(self, model_to, model_from, iter_from, iter_to):
        if model_to == model_from and iter_from== iter_from:
            return False
        else:
            return True
        
    
    def init_populate(self):        
        model = self.get_model().get_model()
        model.clear()
        
        def id(row):
            return row.__hash__()
        
        for i, item in enumerate(["zero", "one"]):
            iter_parent = model.append(None, [i, "P_" + item, True, "bold", None, None])
            model.set_value(iter_parent, POS_level, id(iter_parent))
            
            for j , item in enumerate(["zero", "one", "two"]):            
                #child_iter1 = model.append(iter_parent, [j, "99ch1_" + item, True, "normal", None, None])
                #model.set_value(child_iter1, POS_level, id(child_iter1))            
                #model.set_value(child_iter1, POS_parent, id(iter_parent))
                                
                child_iter = model.append(iter_parent, [j, "ch1_" + item, True, "bold", None, None])
                model.set_value(child_iter, POS_level, id(child_iter))            
                model.set_value(child_iter, POS_parent, id(iter_parent))
                for n , item in enumerate(["++zero", "++one", "++two"]):                    
                    ch1 = model.append(child_iter, [n * i * j, "ch2_" + item, True, "normal", None, None])
                    model.set_value(ch1, POS_level, id(ch1))            
                    model.set_value(ch1, POS_parent, id(child_iter))
        self.expand_all()
   
    def iter_copy(self, from_model, from_iter, to_model, to_iter, pos):
        row = []   
        for i, type in enumerate(self.model_types):
            row.append(from_model.get_value(from_iter, i))
        
        if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            font =  to_model.get_value(to_iter, POS_font)            
            if font == "normal":
                return False
            
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
        return True
    
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
        
        """do not copy to himself"""
        if to_tree == from_tree and from_path == to_path:
            drag_context.finish(False, False)
            return None
        
        """do not copy to child"""        
        result = self.iter_copy(from_model, from_iter, to_model, to_iter, to_pos)
        
        if result and to_tree == from_tree:
            """move element in the save tree"""
            drag_context.finish(True, True)
        
        if to_path:
            to_tree.expand_to_path(to_path)
   
    def print_row(self, row):
        print row, row[0], row[1], row[2], row[3], row[POS_level], row[POS_parent]
    
    def recursion(self, row, plain):
        for child in row.iterchildren():
                self.print_row(child)
                plain.append(child)
                                   
                self.recursion(child, plain)
    
    def plaine_view(self):
        model = self.get_model().get_model()        
        plain = []
        """PLAIN VIEW"""
        for row in model:
            plain.append(row)
            self.print_row(row)
                   
            self.recursion(row, plain)
        
        copy_plain = []
        for row in plain:            
            copy_plain.append(Bean(row))
            
        model.clear()
        
        print "================"
        for bean in copy_plain:
            bean.visible = True
            if bean.font == "bold":
                bean.visible = True
            else:
                bean.visible = True
                
            model.append(None, bean.get_row())
                
    
    def tree_view(self):
        print """TREE VIEW"""
        
        model = self.get_model().get_model()
        print "init size", len(model)        
        plain = []
        for row in model:
            self.print_row(row)
            plain.append(row)
            self.recursion(row, plain)
        
        print "plain size", len(plain)
        print len(plain)
        
        copy_plain = []
        for row in plain:
            bean = Bean(row)
            copy_plain.append(bean)
        
        model.clear()
        print "copy_plain size", len(copy_plain)        
        print """POPULATE"""
        for bean in copy_plain:
            print bean.text, bean.level, bean.parent, bean.font
            self.append_like_tree(bean)
    
        self.expand_all()
    """parent id, parent iter"""
    hash = {None:None}
            
    def append_like_tree(self, bean):
        """copy beans"""
        bean = copy.copy(bean)
        model = self.get_model().get_model()   
        
        if self.hash.has_key(bean.parent):
            parent_iter_exists = self.hash[bean.parent]
        else:
            parent_iter_exists = None
        bean.visible= True
        parent_iter = model.append(parent_iter_exists, bean.get_row())
            
        self.hash[bean.level] = parent_iter

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
        
        scroll_one = gtk.ScrolledWindow()
        one = TreeOne()
        scroll_one.add(one)
        two = TreeTwo()
        
        def on_plain(*a):
            #two.plaine_view()
            one.plaine_view()
        
        def on_tree(*a):
            one.tree_view()
            #two.tree_view()
        
        vbox = gtk.VBox(False, 0)
        
        hbox = gtk.HBox(False, 0)        
        hbox.pack_start(scroll_one)
        hbox.pack_start(two)
        
        hbox1 = gtk.HBox(False, 0)
        to_plain = gtk.Button("Plain")
        to_plain.connect("clicked", on_plain)
        
        to_tree = gtk.Button("Tree")
        to_tree.connect("clicked", on_tree)
         
        hbox1.pack_start(to_plain)
        hbox1.pack_start(to_tree)

        vbox.pack_start(hbox)
        vbox.pack_start(hbox1, False, False)
        
        window.add(vbox)
        window.show_all()

if __name__ == "__main__":
    TwoTreeExample()
    gtk.main()
