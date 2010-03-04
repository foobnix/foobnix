#!/usr/bin/env python

import os, stat, time
import pygtk
pygtk.require('2.0')
import gtk

folderxpm = [
    "17 16 7 1",
    "  c #000000",
    ". c #808000",
    "X c yellow",
    "o c #808080",
    "O c #c0c0c0",
    "+ c white",
    "@ c None",
    "@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@",
    "@@+XXXX.@@@@@@@@@",
    "@+OOOOOO.@@@@@@@@",
    "@+OXOXOXOXOXOXO. ",
    "@+XOXOXOXOXOXOX. ",
    "@+OXOXOXOXOXOXO. ",
    "@+XOXOXOXOXOXOX. ",
    "@+OXOXOXOXOXOXO. ",
    "@+XOXOXOXOXOXOX. ",
    "@+OXOXOXOXOXOXO. ",
    "@+XOXOXOXOXOXOX. ",
    "@+OOOOOOOOOOOOO. ",
    "@                ",
    "@@@@@@@@@@@@@@@@@",
    "@@@@@@@@@@@@@@@@@"
    ]
folderpb = gtk.gdk.pixbuf_new_from_xpm_data(folderxpm)

filexpm = [
    "12 12 3 1",
    "  c #000000",
    ". c #ffff04",
    "X c #b2c0dc",
    "X        XXX",
    "X ...... XXX",
    "X ......   X",
    "X .    ... X",
    "X ........ X",
    "X .   .... X",
    "X ........ X",
    "X .     .. X",
    "X ........ X",
    "X .     .. X",
    "X ........ X",
    "X          X"
    ]
filepb = gtk.gdk.pixbuf_new_from_xpm_data(filexpm)

class FileListModel(gtk.GenericTreeModel):
    column_types = (gtk.gdk.Pixbuf, str, long, str, str)
    column_names = ['Name', 'Size', 'Mode', 'Last Changed']

    def __init__(self, dname=None):
        gtk.GenericTreeModel.__init__(self)
        if not dname:
            self.dirname = os.path.expanduser('~')
        else:
            self.dirname = os.path.abspath(dname)
        self.files = [f for f in os.listdir(self.dirname) if f[0] <> '.']
        self.files.sort()
        self.files = ['..'] + self.files
        return

    def get_pathname(self, path):
        filename = self.files[path[0]]
        return os.path.join(self.dirname, filename)

    def is_folder(self, path):
        filename = self.files[path[0]]
        pathname = os.path.join(self.dirname, filename)
        filestat = os.stat(pathname)
        if stat.S_ISDIR(filestat.st_mode):
            return True
        return False

    def get_column_names(self):
        return self.column_names[:]

    def on_get_flags(self):
        return gtk.TREE_MODEL_LIST_ONLY|gtk.TREE_MODEL_ITERS_PERSIST

    def on_get_n_columns(self):
        return len(self.column_types)

    def on_get_column_type(self, n):
        return self.column_types[n]

    def on_get_iter(self, path):
        return self.files[path[0]]

    def on_get_path(self, rowref):
        return self.files.index(rowref)

    def on_get_value(self, rowref, column):
        fname = os.path.join(self.dirname, rowref)
        try:
            filestat = os.stat(fname)
        except OSError:
            return None
        mode = filestat.st_mode
        if column is 0:
            if stat.S_ISDIR(mode):
                return folderpb
            else:
                return filepb
        elif column is 1:
            return rowref
        elif column is 2:
            return filestat.st_size
        elif column is 3:
            return oct(stat.S_IMODE(mode))
        return time.ctime(filestat.st_mtime)

    def on_iter_next(self, rowref):
        try:
            i = self.files.index(rowref)+1
            return self.files[i]
        except IndexError:
            return None

    def on_iter_children(self, rowref):
        if rowref:
            return None
        return self.files[0]

    def on_iter_has_child(self, rowref):
        return False

    def on_iter_n_children(self, rowref):
        if rowref:
            return 0
        return len(self.files)

    def on_iter_nth_child(self, rowref, n):
        if rowref:
            return None
        try:
            return self.files[n]
        except IndexError:
            return None

    def on_iter_parent(child):
        return None

class GenericTreeModelExample:
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False
 
    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
 
        self.window.set_size_request(300, 200)
 
        self.window.connect("delete_event", self.delete_event)
 
        self.listmodel = FileListModel()
 
        # create the TreeView
        self.treeview = gtk.TreeView()
 
        # create the TreeViewColumns to display the data
        column_names = self.listmodel.get_column_names()
        self.tvcolumn = [None] * len(column_names)
        cellpb = gtk.CellRendererPixbuf()
        self.tvcolumn[0] = gtk.TreeViewColumn(column_names[0],
                                              cellpb, pixbuf=0)
        cell = gtk.CellRendererText()
        self.tvcolumn[0].pack_start(cell, False)
        self.tvcolumn[0].add_attribute(cell, 'text', 1)
        self.treeview.append_column(self.tvcolumn[0])
        for n in range(1, len(column_names)):
            cell = gtk.CellRendererText()
            if n == 1:
                cell.set_property('xalign', 1.0)
            self.tvcolumn[n] = gtk.TreeViewColumn(column_names[n],
                                                  cell, text=n+1)
            self.treeview.append_column(self.tvcolumn[n])

        self.treeview.connect('row-activated', self.open_file)
        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.add(self.treeview)
        self.window.add(self.scrolledwindow)
        self.treeview.set_model(self.listmodel)
        self.window.set_title(self.listmodel.dirname)
        self.window.show_all()

    def open_file(self, treeview, path, column):
        model = treeview.get_model()
        if model.is_folder(path):
            pathname = model.get_pathname(path)
            new_model = FileListModel(pathname)
            self.window.set_title(new_model.dirname)
            treeview.set_model(new_model)
        return
 
def main():
    gtk.main()

if __name__ == "__main__":
    gtmexample = GenericTreeModelExample()
    main()
