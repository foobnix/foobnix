#-*- coding: utf-8 -*-
'''
Created on Sep 23, 2010

@author: ivan
'''
import gtk
from foobnix.util import LOG, const
from foobnix.helpers.my_widgets import tab_close_button, notetab_label
#from foobnix.online.online_model import OnlineListModel
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl
from foobnix.regui.state import LoadSave
from foobnix.regui.model import FModel
import thread
from foobnix.regui.treeview.playlist_tree import PlaylistTreeControl
from foobnix.util.mouse_utils import is_double_left_click
from foobnix.util.file_utils import get_file_path_from_dnd_dropped_uri

TARGET_TYPE_URI_LIST = 80
dnd_list = [ ('text/uri-list', 0, TARGET_TYPE_URI_LIST) ]

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
        
        self.set_show_border(True)
        self.set_scrollable(True)
        
        self.connect('drag-data-received', self.on_system_drag_data_received)
        self.drag_dest_set(gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_DROP, dnd_list, gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_COPY)
        
        #self.connect("button-press-event", self.on_button_press)
       
        self.empty_tab()
        
    def on_system_drag_data_received(self, widget, context, x, y, selection, target_type, timestamp):
        if target_type == TARGET_TYPE_URI_LIST:
            uri = selection.data.strip('\r\n\x00')
            uri_splitted = uri.split() # we may have more than one file dropped
            paths = []
            for uri in uri_splitted:
                path = get_file_path_from_dnd_dropped_uri(uri)
                paths.append(path)
            
            self.controls.check_for_media(paths)
    """
    def on_select_page(self,tab, pointer, num):
        current = self.get_current_page()
        if current >0:
            self.active_tree = self.get_children()[current].get_children()[0]
    """
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            self.empty_tab()
            
    def create_plus_tab(self):
        append_label = notetab_label(func=self.empty_tab, arg=None, angel=0, symbol="+")
        l = notetab_label(func=self.empty_tab, arg=None, angel=0, symbol="Click me")
        self.prepend_page(l, append_label)
        
    def empty_tab(self, *a):
        self.append_tab("Foobnix tab", [])
    
    def get_active_tree(self):
        return self.active_tree
    
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
                return notetab_label(func=self.on_delete_tab, arg=tab_content, angel=self.default_angel)

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
        self.create_plus_tab()
        if self.get_n_pages() >= 2:
            self.remove_page(2)
        
        self.set_current_page(1)

        if self.get_n_pages() > FC().count_of_tabs:
            self.remove_page(self.get_n_pages() - 1)
        
        """autostart play"""
        #if beans:
        #    self.controls.next()
    
    def update_label_angel(self, angle):
        for label in self.tab_labes:
            label.set_angle(angle)
    
    def set_tab_left(self):
        LOG.info("Set tabs Left")
        self.set_tab_pos(gtk.POS_LEFT)
        self.update_label_angel(90)
        self.default_angel = 90
        self.set_show_tabs(True)
        FC().tab_position = "left"

        for box in self.tab_hboxes:
            box.hide()

        for box in self.tab_vboxes:
            box.show()

    def set_tab_top(self):
        LOG.info("Set tabs top")
        self.set_tab_pos(gtk.POS_TOP)
        self.update_label_angel(0)
        self.default_angel = 0
        self.set_show_tabs(True)
        FC().tab_position = "top"
        for box in self.tab_hboxes:
            box.show()

        for box in self.tab_vboxes:
            box.hide()


    def set_tab_no(self):
        LOG.info("Set tabs no")
        self.set_show_tabs(False)
        FC().tab_position = "no"
        for box in self.tab_hboxes:
            box.hide()

        for box in self.tab_vboxes:
            box.hide()

    
    def next(self):
        bean = self.active_tree.next(random=self.is_random, lopping=self.lopping)
        print "Next notetab", bean
        if not bean.is_file:
            return self.next()
        return bean

    def prev(self):
        bean = self.active_tree.prev(rnd=self.is_random, lopping=self.lopping)
        print "Prev notetab", bean
        if not bean.is_file:
            return self.prev()
        return bean

    def create_notebook_tab(self, beans):

        treeview = PlaylistTreeControl(self.controls)
        self.switch_tree(treeview)

        #treeview.populate_from_scanner(beans)
        #if beans:
        #    treeview.populate(beans)
        if beans:
            for bean in beans:         
                treeview.append(bean)
            
        window = gtk.ScrolledWindow()
        window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        #window.add_with_viewport(treeview)
        window.add(treeview)
        window.show_all()

        return  window

    def append(self, beans):
        for bean in beans:
            self.active_tree.append(bean)
        self.get_active_tree().expand_all() 

    def on_delete_tab(self, child):
        n = self.page_num(child)    
        if n > 0:    
            self.delete_tab(n)

    def delete_tab(self, page=None):
        if not page:
            LOG.info("Remove current page")
            page = self.get_current_page()
        self.remove_page(page)

    def set_random(self, flag):
        self.is_random = flag

    def set_lopping_all(self):
        self.lopping = const.LOPPING_LOOP_ALL
        print self.lopping

    def set_lopping_single(self):
        self.lopping = const.LOPPING_SINGLE
        print self.lopping

    def set_lopping_disable(self):
        self.lopping = const.LOPPING_DONT_LOOP
        print self.lopping

    def on_load(self):
        self.is_random = FC().is_order_random
        self.lopping = FC().lopping

    def on_save(self):
        FC().is_order_random = self.is_random
        FC().lopping = self.lopping

    def switch_tree(self, tree):
        self.active_tree = tree

    def set_playlist_tree(self):
        self.active_tree.set_playlist_tree()

    def set_playlist_plain(self):
        self.active_tree.set_playlist_plain()

