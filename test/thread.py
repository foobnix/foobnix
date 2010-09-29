"""
 Copyright (C) 2009, Eduardo Silva P <edsiper@gmail.com>

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; either version 2 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Library General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
"""

import gtk
import gobject
import random
import threading

class TV(gtk.ScrolledWindow):
    def __init__(self, model):
        gtk.ScrolledWindow.__init__(self)

        self._last_col_index = 0
        self.model = model
        self.treeview = gtk.TreeView()
               
        # create filter
        self.filter = model.filter_new()
        self.filter.set_visible_func(self._cb_visible, [0])

        # sorter
        self.sorter = gtk.TreeModelSort(self.filter)
        self.treeview.set_model(self.sorter)

        self.add(self.treeview)
        
    def add_column(self, column_name):
        cell = gtk.CellRendererText()

        # Configurable wrap
        col_tv = gtk.TreeViewColumn(column_name, cell, text=self._last_col_index)
        
        self.treeview.append_column(col_tv)


    def _cb_visible(self, model, iter, idx):
        return True

class _IdleObject(gobject.GObject):
    """
    Override gobject.GObject to always emit signals in the main thread
    by emmitting on an idle handler
    """
    def __init__(self):
        gobject.GObject.__init__(self)

    def emit(self, *args):
        gobject.idle_add(gobject.GObject.emit,self,*args)

class Data(_IdleObject):
    __gsignals__ =  { 
        "data": (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
            (gobject.TYPE_PYOBJECT,))
        }
    def __init__(self):
       _IdleObject.__init__(self)

    def run(self):
        d = list()
        for i in range(0,20):
            n = random.random()
            d.append(n)

        self.emit('data', d)

class Thread(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self._data = data

    def run(self):
        self._data.run()

class Main(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)

        self.ts  = gtk.ListStore(str)
        tv = TV(self.ts)
        tv.add_column('Data')
        button = gtk.Button('Populate')
        button.connect('clicked', self.launch_thread)

        self.data = Data()
        self.data.connect('data', self._populate)

        vbox = gtk.VBox()
        vbox.pack_start(tv)
        vbox.pack_start(button, False)

        self.set_size_request(500, 400)
        self.add(vbox)
        self.show_all()

    def _populate(self, object, values):
        self.ts.clear()
        for val in values:
            self.ts.append([str(val)])

    def launch_thread(self, widget):
        thread = Thread(self.data)
        thread.start()

gobject.threads_init()
main = Main()
gtk.main()
        
            
    
