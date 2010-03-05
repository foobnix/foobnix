#!/usr/bin/env python

# example treemodelfilter.py

import pygtk
pygtk.require('2.0')
import gtk

bugdata = """120595 1 Custom GtkTreeModelFilter wrappers need
121339 2 dsextras.py installation directory is incorrect
121611 3 argument is guint, should be guint32
121943 4 gtk.mainiteration and gtk.mainloop defeat the caller's ex...
122260 5 Could not compile"""

class TreeModelFilterExample:

    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def __init__(self):
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("TreeModelFilter Example")
        self.window.set_size_request(400, 400)
        self.window.connect("delete_event", self.delete_event)


        # create a listStore with one string column to use as the model
        self.listStore = gtk.TreeStore(str, str, str)
        
        
        self.modelFilter = self.listStore.filter_new()

        # create the TreeView
        self.treeView = gtk.TreeView()

        # create the TreeViewColumns to display the data
        self.treeView.columns = [None] * 3
        self.treeView.columns[0] = gtk.TreeViewColumn('Bug No.')
        self.treeView.columns[1] = gtk.TreeViewColumn('Status')
        self.treeView.columns[2] = gtk.TreeViewColumn('Description')

        # add bug data
        self.states = []
        
        a = self.listStore.append(None, [11, 21, 31])
        b = self.listStore.append(None, [12, 22, 32])
        c = self.listStore.append(None, [13, 23, 33])
        
        a = self.listStore.append(a, [111, 121, 131])
        b = self.listStore.append(b, [112, 122, 132])
        c = self.listStore.append(c, [113, 123, 133])
        
        a = self.listStore.append(a, [1111, 1121, 1131])
        b = self.listStore.append(b, [1112, 1122, 1132])
        c = self.listStore.append(c, [1113, 1123, 1133])
        
        self.show_states = self.states[:]        
        self.modelFilter.set_visible_func(self.visible_cb, self.show_states)

        self.treeView.set_model(self.modelFilter)
        
        
        for n in range(3):
            # add columns to treeView
            self.treeView.append_column(self.treeView.columns[n])
            # create a CellRenderers to render the data
            self.treeView.columns[n].cell = gtk.CellRendererText()
            # add the cells to the columns
            self.treeView.columns[n].pack_start(self.treeView.columns[n].cell,
                                                True)
            # set the cell attributes to the appropriate listStore column
            self.treeView.columns[n].set_attributes(
                self.treeView.columns[n].cell, text=n)


        # make treeView searchable
        self.treeView.set_search_column(3)

        # make ui layout
        self.vbox = gtk.VBox()
        self.scrolledwindow = gtk.ScrolledWindow()
        self.bbox = gtk.HButtonBox()
        self.vbox.pack_start(self.scrolledwindow)
        self.vbox.pack_start(self.bbox, False)
        # create toggle buttons to select filtering based on
        # bug state and set buttons active
        for state in self.states:
            b = gtk.ToggleButton(state)
            self.bbox.pack_start(b)
            b.set_active(True)
            b.connect('toggled', self.check_buttons)

        self.scrolledwindow.add(self.treeView)
        self.window.add(self.vbox)
        self.window.show_all()
        
        for row in self.listStore:            
            print row[0]            
            self.getALLChildren(row)
        return
    
    def getALLChildren(self, row):
        for child in row.iterchildren():
                print child[0]
                self.getALLChildren(child)
        

    # visibility determined by state matching active toggle buttons
    def visible_cb(self, model, iter, data):
        return model.get_value(iter, 1) in data

    # build list of bug states to show and then refilter
    def check_buttons(self, tb):
        del self.show_states[:]
        for b in self.bbox.get_children():
            if b.get_active():
                self.show_states.append(b.get_label())
        self.modelFilter.refilter()
        return

def main():
    gtk.main()

if __name__ == "__main__":
    tmfexample = TreeModelFilterExample()
    main()
