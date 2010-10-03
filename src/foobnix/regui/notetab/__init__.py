#-*- coding: utf-8 -*-
'''
Created on Sep 23, 2010

@author: ivan
'''
import gtk
from foobnix.util import LOG
from foobnix.helpers.my_widgets import tab_close_button, tab_close_label
from foobnix.online.online_model import OnlineListModel
from foobnix.util.fc import FC
from foobnix.regui.treeview.playlist import PlaylistControl
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
from foobnix.regui.model import FModel
from foobnix.regui.treeview.scanner import DirectoryScanner
from foobnix.regui.treeview.musictree import MusicTreeControl
import thread
class NoteTabControl(gtk.Notebook, FControl, LoadSave):
    def __init__(self, controls):
        gtk.Notebook.__init__(self)
        FControl.__init__(self, controls)

        self.default_angel = 0
        self.tab_labes = []
        self.tab_vboxes = []
        self.tab_hboxes = []
        self.last_notebook_page = ""
        self.last_notebook_beans = []
        self.active_tree = None

        self.append_tab("Foobnix", [])

    def append_tab(self, name, beans=None):
        self.last_notebook_page = name
        LOG.info("append new tab")
        if name and len(name) > FC().len_of_tab:
            name = name[:FC().len_of_tab]

        tab_content = self.create_notebook_tab(beans)
        def label():
            """label"""
            label = gtk.Label(name + " ")
            label.show()
            label.set_angle(self.default_angel)
            self.tab_labes.append(label)
            return label

        def button():
            print "ELEMENT", FC().tab_close_element
            if FC().tab_close_element == "button":
                return tab_close_button(func=self.on_delete_tab, arg=tab_content)
            else:
                return tab_close_label(func=self.on_delete_tab, arg=tab_content, angel=self.default_angel)

        """container Vertical Tab"""
        vbox = gtk.VBox(False, 0)
        if  self.default_angel == 90:
            vbox.show()
        vbox.pack_start(button(), False, False, 0)
        vbox.pack_start(label(), False, False, 0)
        self.tab_vboxes.append(vbox)

        """container Horizontal Tab"""
        hbox = gtk.HBox(False, 0)
        if  self.default_angel == 0:
            hbox.show()
        hbox.pack_start(label(), False, False, 0)
        hbox.pack_start(button(), False, False, 0)
        self.tab_hboxes.append(hbox)

        """container BOTH"""
        both = gtk.HBox(False, 0)
        both.show()
        both.pack_start(vbox, False, False, 0)
        both.pack_start(hbox, False, False, 0)

        """append tab"""
        self.prepend_page(tab_content, both)
        self.set_current_page(0)

        if self.get_n_pages() > FC().count_of_tabs:
            self.remove_page(self.get_n_pages() - 1)
        
        """autostart play"""
        if beans:
            self.controls.next()

    def next(self):
        return self.active_tree.next(rnd=self.isRandom)

    def prev(self):
        return self.active_tree.prev(rnd=self.isRandom)

    def create_notebook_tab(self, beans):

        treeview = PlaylistControl(self.controls)
        self.switch_tree(treeview)

        #treeview.populate_from_scanner(beans)
        if beans:
            treeview.populate(beans)
        #for bean in beans:
            #bean.level = None
        #    treeview.append(bean)
        window = gtk.ScrolledWindow()
        window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        #window.add_with_viewport(treeview)
        window.add(treeview)
        window.show_all()

        return  window

    def append(self, beans):
        for bean in beans:
            self.active_tree.append(bean)

    def on_delete_tab(self, widget, event, child):
        if event.type == gtk.gdk.BUTTON_PRESS: #@UndefinedVariable
            n = self.page_num(child)
            self.delete_tab(n)

    def delete_tab(self, page=None):
        if not page:
            LOG.info("Remove current page")
            page = self.get_current_page()
        self.remove_page(page)

    def set_random(self, flag):
        self.isRandom = flag

    def on_load(self):
        self.isRandom = FC().is_order_random

    def on_save(self):
        pass

    def switch_tree(self, tree):
        if self.active_tree and self.active_tree != tree:
            self.active_tree.repopulate(-1)
        self.active_tree = tree