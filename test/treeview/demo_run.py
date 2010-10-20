#-*- coding: utf-8 -*-
'''
Created on 10 окт. 2010

@author: ivan
'''
import gtk
from foobnix.regui.model import FModel
from foobnix.regui.treeview.common_tree import CommonTreeControl

class BaseTree(CommonTreeControl):
    def __init__(self, title):            
        CommonTreeControl.__init__(self, title)
        
        """column config"""
        self.column = gtk.TreeViewColumn("Left Renderer", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        self.column.set_resizable(True)
        self.append_column(self.column)
        self.set_headers_visible(True)
        
        
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
