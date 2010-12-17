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
import gobject
from foobnix.util.tab_utils import get_text_label_from_tab
import time

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
        self.drag_dest_set(gtk.DEST_DEFAULT_MOTION | gtk.DEST_DEFAULT_DROP, dnd_list, gtk.gdk.ACTION_MOVE | gtk.gdk.ACTION_COPY) #@UndefinedVariable
        
        if not FC().cache_pl_tab_contents:
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
   
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            self.empty_tab()
            
    def create_plus_tab(self):
        if self.get_n_pages() > 1:
            print "self.page_num(self.plus_tab_child): ", self.page_num(self.plus_tab_child)
            self.reorder_child(self.plus_tab_child, 0)
            print "self.page_num(self.plus_tab_child): ", self.page_num(self.plus_tab_child)
            print "after rechild: ", self.get_current_page()
            print "in create plus tab: ", self.get_current_page()
            return
        append_label = notetab_label(func=self.empty_tab, arg=None, angel=0, symbol="+")
        self.plus_tab_child = notetab_label(func=self.empty_tab, arg=None, angel=0, symbol="Click me")
        self.prepend_page(self.plus_tab_child, append_label)
        
        
    def empty_tab(self, *a):
        self.append_tab("Foobnix", None, [])
    
    def get_active_tree(self):
        return self.active_tree
    
    def append_tab(self, name, tab_content = None, beans=None):
        
        #def task():
        self._append_tab(name, tab_content, beans)
        #gobject.idle_add(task)
        
    
    def _append_tab(self, name, tab_content = None, beans=None):
        print "in _append_tab"
        self.last_notebook_page = name
        LOG.info("append new tab")
        try:
            LOG.info("encoding of tab name is", name)
            name = unicode(name) #convert from any encoding in ascii
            LOG.info("encoding finished ", name)
        except:
            LOG.warn("problem of encoding definition for tab name is occured")
        
        if name and (FC().len_of_tab > -1) and (len(name) > FC().len_of_tab):
            name = name[:FC().len_of_tab]
        
        if not tab_content:
            tab_content = self.create_notebook_tab(beans)
        
        def label():
            """label"""
            label = gtk.Label(name + " ")
            label.show()
            label.set_angle(self.default_angel)
            self.tab_labes.append(label)
            return label

                    
        """container Vertical Tab"""
        vbox = gtk.VBox(False, 0)
        if  self.default_angel == 90:
            vbox.show()
        if FC().tab_close_element:
            vbox.pack_start(self.button(tab_content), False, False, 0)
        vbox.pack_end(label(), False, False, 0)
        self.tab_vboxes.append(vbox)

        """container Horizontal Tab"""
        hbox = gtk.HBox(False, 0)
        if  self.default_angel == 0:
            hbox.show()
        if FC().tab_close_element:
            hbox.pack_end(self.button(tab_content), False, False, 0)
        hbox.pack_start(label(), False, False, 0)
                        
        self.tab_hboxes.append(hbox)
        
        """container BOTH"""
        box = vbox if FC().tab_position == "left" else hbox
        event = self.to_eventbox(box)
        event.connect("button-press-event", self.button_press, tab_content)  
        
        """append tab"""
        
        self.prepend_page(tab_content, event)
        print self.get_current_page()
        time.sleep(2)
        self.set_tab_reorderable(tab_content, True)
        #self.set_tab_label_packing(tab_content, False, True, gtk.PACK_END)
        self.create_plus_tab()
        print self.get_current_page()
        time.sleep(2)
        #self.set_current_page(1)
        print self.get_current_page()
        time.sleep(2)
        if self.get_n_pages() - 1 > FC().count_of_tabs:
            self.remove_page(self.get_n_pages() - 1)
        print self.get_current_page()
        time.sleep(2)
        self.set_current_page(1)
        self.show_all()    
    
    def button(self, tab_content):
            if FC().tab_close_element == "button":
                return tab_close_button(func=self.on_delete_tab, arg=tab_content)
            else:
                return notetab_label(func=self.on_delete_tab, arg=tab_content, angel=self.default_angel)
    
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
        for page in xrange(self.get_n_pages()-1, 0, -1):
            tab_content = self.get_nth_page(page)
            label_text = get_text_label_from_tab(self, tab_content)
            vbox = gtk.VBox()
            label = gtk.Label(label_text)
            label.set_angle(90)
            if FC().tab_close_element:
                vbox.pack_start(self.button(tab_content), False, False, 0)
            vbox.pack_end(label, False, False, 0)
            event = self.to_eventbox(vbox)
            self.set_tab_label(tab_content, event)
        
    def set_tab_top(self):
        LOG.info("Set tabs top")
        self.set_tab_pos(gtk.POS_TOP)
        self.update_label_angel(0)
        self.default_angel = 0
        self.set_show_tabs(True)
        FC().tab_position = "top"
        for page in xrange(self.get_n_pages()-1, 0, -1):
            tab_content = self.get_nth_page(page)
            label_text = get_text_label_from_tab(self, tab_content)
            hbox = gtk.HBox()
            label = gtk.Label(label_text)
            label.set_angle(0)
            if FC().tab_close_element:
                hbox.pack_end(self.button(tab_content), False, False, 0)
            hbox.pack_start(label, False, False, 0)
            event = self.to_eventbox(hbox)
            self.set_tab_label(tab_content, event)
        
    def set_tab_no(self):
        LOG.info("Set tabs no")
        self.set_show_tabs(False)
        FC().tab_position = "no"
        for box in self.tab_hboxes:
            box.hide()

        for box in self.tab_vboxes:
            box.hide()

    
    def next(self):
        bean = self.active_tree.next()
        return bean

    def prev(self):
        bean = self.active_tree.prev()
        return bean

    def create_notebook_tab(self, beans):
        treeview = PlaylistTreeControl(self.controls)
        self.set_active_tree(treeview)
        treeview.append_all(beans)
        treeview.scroll.show_all()
        return  treeview.scroll

    def append_all(self, beans):
        self.active_tree.append_all(beans)
    
    def on_delete_tab(self, child):
        n = self.page_num(child)    
        self.delete_tab(n)

    def delete_tab(self, page=None):
        if not page:
            LOG.info("Remove current page")
            page = self.get_current_page()
        self.remove_page(page)
    
    def on_load(self):
        if FC().tab_position == "no": self.set_tab_no()
        elif FC().tab_position == "left": self.set_tab_left()
        else: self.set_tab_top()
        print "in on_load"
        print "FC().cache_pl_tab_contents: ",FC().cache_pl_tab_contents
        print len(FC().cache_pl_tab_contents)
        for page in xrange(0, len(FC().cache_pl_tab_contents)):
            if FC().cache_pl_tab_contents[page] == []:
                print "in if"
                self.append_tab(FC().tab_pl_names[page], None, None)
                continue
            print "in cycle of  on_load"
            #print "page: ", page
            print  "FC().tab_pl_names: ", FC().tab_pl_names 
            print "FC().cache_pl_tab_contents[page-1]: ",FC().cache_pl_tab_contents[page]
            self.controls.append_to_new_notebook(FC().tab_pl_names[page], FC().cache_pl_tab_contents[page])
            #self.append_tab(FC().tab_pl_names[page], None, FC().cache_pl_tab_contents[page])
            

    def on_save(self):
        number_music_tabs = self.get_n_pages()-1
        print "number_music_tabs: ", number_music_tabs
        FC().cache_pl_tab_contents = []
        FC().tab_pl_names = []
        if number_music_tabs > 0:
            for page in xrange(number_music_tabs, 0, -1):
                print "page: ", page
                tab_content = self.get_nth_page(page)
                pl_tree = tab_content.get_child()
                beans = pl_tree.get_all_beans()
                
                print "FC().cache_pl_tab_contents: befor", FC().cache_pl_tab_contents
                
                """if beans:
                    FC().cache_pl_tab_contents.insert(0, [])
                    for bean in beans:
                        print "FC().cache_pl_tab_contents after: ", FC().cache_pl_tab_contents"""
                #FC().cache_pl_tab_contents.insert(0, beans)
                FC().cache_pl_tab_contents.append(beans)
                        #elif bean.text:
                            #FC().cache_pl_tab_contents[0].append(bean.path)   
                #FC().cache_pl_tab_contents.insert(1, tab_content)
                #FC().tab_pl_names.insert(0, get_text_label_from_tab(self, tab_content))
                FC().tab_pl_names.append(get_text_label_from_tab(self, tab_content))
    def set_active_tree(self, tree):
        self.active_tree = tree

    def set_playlist_tree(self):
        self.active_tree.set_playlist_tree()

    def set_playlist_plain(self):
        self.active_tree.set_playlist_plain()

    def to_eventbox(self, widget):
        event = gtk.EventBox()
        event.add(widget)
        event.set_visible_window(False)
        event.show_all()
        return event
    
    def button_press(self, w, e, tab_content):
        print self.page_num(tab_content)
        print "tab_content is:", tab_content
        print self.get_tab_label(tab_content)
        print self.get_tab_label(tab_content).get_child()
        