#-*- coding: utf-8 -*-
'''
Created on 10 окт. 2010

@author: ivan
'''
import gtk
from foobnix.regui.treeview import TreeViewControl
from foobnix.regui.model import FModel
import copy
import uuid
from sets import Set

VIEW_PLAIN = 0
VIEW_TREE = 1

class BaseTree(TreeViewControl):
    def __init__(self, title):            
        TreeViewControl.__init__(self, title)
        
        """column config"""
        self.column = gtk.TreeViewColumn("Left Renderer", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        self.column.set_resizable(True)
        self.append_column(self.column)
        self.set_headers_visible(True)
        
        """init values"""
        self.hash = {None:None}
        self.current_view = None
        
    def updates_tree_structure(self):
        for row in self.model:
            row[self.parent_level[0]] = None
            row[self.level[0]] = uuid.uuid4().hex             
            self.update_tree_structure_row_requrcive(row)
    
    def update_tree_structure_row_requrcive(self, row):        
        for child in row.iterchildren():
                child[self.parent_level[0]] = row[self.level[0]]
                child[self.level[0]] = uuid.uuid4().hex   
                self.update_tree_structure_row_requrcive(child)
   
    def iter_copy(self, from_model, from_iter, to_model, to_iter, pos):
        
        row = self.get_row_from_model_iter(from_model, from_iter)
        
        if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            is_file = to_model.get_value(to_iter, self.is_file[0])
            if is_file == True:
                return False
            
            new_iter = to_model.prepend(to_iter, row)               
        elif pos == gtk.TREE_VIEW_DROP_BEFORE:
            new_iter = to_model.insert_before(None, to_iter, row)
        elif pos == gtk.TREE_VIEW_DROP_AFTER:
            new_iter = to_model.insert_after(None, to_iter, row)
        else:
            new_iter = to_model.append(None, row)
        
        """tree to tree"""
        #if from_model.iter_has_child(from_iter):
        #    for i in range(0, from_model.iter_n_children(from_iter)):
        #        next_iter_to_copy = from_model.iter_nth_child(from_iter, i)
        #        self.iter_copy(from_model, next_iter_to_copy, to_model, new_iter, gtk.TREE_VIEW_DROP_INTO_OR_BEFORE)
        
        
        """plain to tree"""
        parent_row = self.get_row_from_model_iter(from_model, from_iter)
        parent_level = parent_row[self.level[0]]
        self.add_reqursive_plain(from_model, from_iter, to_model, new_iter, parent_level)
        
        """tree to plain"""
        
        """plain to plain"""
        
        
        return True
    
    def add_reqursive_plain(self, from_model, from_iter, to_model, to_iter, parent_level):
        for child_row in self.get_child_rows(from_model, parent_level):            
            new_iter = to_model.append(to_iter, child_row)
            child_level = child_row[self.level[0]]
            self.add_reqursive_plain(from_model, from_iter, to_model, new_iter, child_level)
    
    def get_child_rows(self, model, parent_level):
        result = []
        for child_row in model:
            if child_row[self.parent_level[0]] == parent_level:
                result.append(child_row)        
        return result
    
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
        
        print "FROM TYPE", from_tree.current_view
        print "TO TY", to_tree.current_view
        
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
        
        self.updates_tree_structure()
   
    def get_widgets(self):
        hbox = gtk.HBox(False, 0)
        to_plain = gtk.Button("Plain")
        to_plain.connect("clicked", self.rebuild_as_plain)
        
        to_tree = gtk.Button("Tree")
        to_tree.connect("clicked", self.rebuild_as_tree)
         
        hbox.pack_start(to_plain)
        hbox.pack_start(to_tree)
        
        vbox = gtk.VBox(False, 0)
        vbox.pack_start(self)
        vbox.pack_start(hbox, False, False)
        
        return vbox
    
    def child_by_recursion(self, row, plain):
        for child in row.iterchildren():
                plain.append(child)
                self.child_by_recursion(child, plain)
    
    def rebuild_as_tree(self, *a):
        self.current_view = VIEW_TREE        
        plain = []
        for row in self.model:
            plain.append(row)
            self.child_by_recursion(row, plain)
        
        copy_beans = []
        for row in plain:
            bean = self.get_bean_from_row(row)
            copy_beans.append(bean)
        
        self.clear()
        
        self.tree_append_all(copy_beans)
    
        self.expand_all()
    
    def rebuild_as_plain(self, *a):
        self.current_view = VIEW_PLAIN
        plain = []
        for row in self.model:
            plain.append(row)
            self.child_by_recursion(row, plain)
        
        copy_beans = []
        for row in plain:
            bean = self.get_bean_from_row(row)
            copy_beans.append(bean)
            
        self.clear()
        
        self.plain_append_all(copy_beans)
        
    def tree_append_all(self, beans):
        self.current_view = VIEW_TREE
        print "append all"
        for bean in beans:
            self.tree_append(bean)
    
    def plain_append_all(self, beans):
        self.current_view = VIEW_PLAIN
        print "append all"
        for bean in beans:
            self.plain_append(bean)
            
    def plain_append(self, bean):
        if bean.is_file == True:
            bean.font = "normal"
        else:
            bean.font = "bold"
            
        bean.visible = True
        bean.index = self.count_index + 1
        row = self.get_row_from_bean(bean)
        self.model.append(None, row)
        
    def tree_append(self, bean):
        if bean.is_file == True:
            bean.font = "normal"
        else:
            bean.font = "bold"
        
        """copy beans"""
        bean = copy.copy(bean)
        bean.visible = True
        bean.index = self.count_index + 1

        if self.hash.has_key(bean.get_parent()):
            parent_iter_exists = self.hash[bean.get_parent()]
        else:
            parent_iter_exists = None
        row = self.get_row_from_bean(bean)
        parent_iter = self.model.append(parent_iter_exists, row)
            
        self.hash[bean.level] = parent_iter
        
    
def init_data():
    list = []
    for i in xrange(2):
        model = FModel()
        model.text = "parent %s" % i 
        model.is_file = False
        model.level = model.get_uuid()
        model.set_parent(None)
        list.append(model)
        
        for j in xrange(2):
            model1 = FModel()
            model1.text = "child %s" % j
            model1.is_file = False
            model1.level = model1.get_uuid()
            model1.set_parent(model.get_level())
            list.append(model1)
            for k in xrange(2):
                model2 = FModel()
                model2.text = "child child %s" % k
                model2.is_file = True
                model2.level = model2.get_uuid()
                model2.set_parent(model1.get_level())
                list.append(model2)
    
    return list    

class LeftList(BaseTree):
    def __init__(self):
        BaseTree.__init__(self, "Left")
        
        self.plain_append_all(init_data())
        
class RigthList(BaseTree):
    def __init__(self):
        BaseTree.__init__(self, "Right")
                
        self.tree_append_all(init_data())
        
    
class TwoTreeExample:
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", gtk.main_quit)
        window.set_default_size(450, 550)
        window.set_position(gtk.WIN_POS_CENTER)
        
        
        left = LeftList().get_widgets()       
        rigth = RigthList().get_widgets()
        
       
        vbox = gtk.VBox(False, 0)
        
        hbox = gtk.HBox(False, 0)        
        hbox.pack_start(left)
        hbox.pack_start(rigth)
        
        vbox.pack_start(hbox)
        
        window.add(vbox)
        window.show_all()

if __name__ == "__main__":
    TwoTreeExample()
    gtk.main()
