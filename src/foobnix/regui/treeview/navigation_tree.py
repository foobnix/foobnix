#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
import gobject

from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click, is_middle_click, is_left_click
from foobnix.regui.state import LoadSave
from foobnix.helpers.menu import Popup
from foobnix.util.fc import FC
from foobnix.util import LOG
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.const import LEFT_PERSPECTIVE_NAVIGATION
from foobnix.util.list_utils import any
    
    
class NavigationTreeControl(CommonTreeControl, LoadSave):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        self.controls = controls
        
        """column config"""
        column = gtk.TreeViewColumn(_("Music Library"), gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.append_column(column)
        
        self.configure_send_drug()
        
        self.set_type_tree()
        self.is_empty = False
        
        selection = self.get_selection()
        selection.connect("changed", self.selection_chanaged)

    def selection_chanaged(self, w):
        paths = self.get_selected_bean_paths()
        if paths != None:
            FC().nav_selected_paths = paths
        else:
            FC().nav_selected_paths = []
    
    def activate_perspective(self):
        FC().left_perspective = LEFT_PERSPECTIVE_NAVIGATION
    
    def on_button_press(self, w, e):
        if is_middle_click(e):
            # on left double click add selected items to current tab
            self.add_to_current_tab()
            return

        if is_left_click(e):
            # on left click expand selected folders
            return
        
        if is_double_left_click(e):
            # on middle click play selected beans 
            self.add_to_new_tab()
            return
        
        if is_rigth_click(e):
            # on right click, show pop-up menu
            menu = Popup()
            menu.add_item(_("Add to current tab"), gtk.STOCK_ADD, self.add_to_current_tab, None)
            menu.add_item(_("Add to new tab"), gtk.STOCK_MEDIA_PLAY, self.add_to_new_tab, None)
            menu.add_separator()
            menu.add_item(_("Add folder"), gtk.STOCK_OPEN, self.add_folder, None)
            menu.add_separator()

            if FC().tabs_mode == "Multi":
                menu.add_item(_("Add folder in new tab"), gtk.STOCK_OPEN, lambda : self.add_folder(True), None)
                menu.add_item(_("Clear Music Tree"), gtk.STOCK_CLEAR, lambda : self.controls.tablib.clear_tree(self.scroll), None)
            menu.add_item(_("Update Music Tree"), gtk.STOCK_REFRESH, lambda: self.controls.tablib.on_update_music_tree(self.scroll), None)
                
            menu.show(e)
    
    def collect_selected_beans(self):
        def is_parent(path_parent, path_child):
            len_parent = len(path_parent)
            len_child = len(path_child)
            if len_child <= len_parent:
                return False
            for i in xrange(0, len_parent):
                if path_parent[i] != path_child[i]:
                    return False
            return True
        
        paths = self.get_selected_bean_paths()
        if not paths:
            return None
        model = self.get_model()
        beans = []
        for path in paths:
            if any(lambda p : is_parent(p, path), paths):
                continue
            iter = model.get_iter(path)
            sub_beans = self.get_child_iters_by_parent(model, iter)
            parent_bean = self._get_bean_by_path(path)            
            beans = beans + [parent_bean] + sub_beans
        return beans       
    
    def add_to_new_tab(self):
        beans = self.collect_selected_beans()
        if not beans:
            return
        selected = self.get_selected_bean()
        self.controls.append_to_new_notebook(selected.text, beans)
        self.controls.play_first_file_in_playlist()
    
    def add_to_current_tab(self):
        beans = self.collect_selected_beans()
        if not beans:
            return
        self.controls.append_to_current_notebook(beans)
        # start play, if not yet playing
        if not self.controls.state_is_playing():
            self.controls.play_first_file_in_playlist()
    
    def add_folder(self, in_new_tab=False):
        chooser = gtk.FileChooserDialog(title=_("Choose directory with music"),
                                        action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_select_multiple(True)
        if FC().last_music_path:
            chooser.set_current_folder(FC().last_music_path)
        response = chooser.run()
        
        if response == gtk.RESPONSE_OK:
            paths = chooser.get_filenames()
            path = paths[0]
            FC().last_music_path = path[:path.rfind("/")]
            tree = self
            number_of_tab = self.controls.tablib.page_num(tree.scroll)
                      
            if in_new_tab:
                tree = NavigationTreeControl(self.controls)
                tab_name = unicode(path[path.rfind("/") + 1:])
                self.controls.tablib.append_tab(tab_name, navig_tree=tree)
                number_of_tab = self.controls.tablib.get_current_page()
                FC().music_paths.insert(0, [])
                FC().tab_names.insert(0, tab_name)
                FC().cache_music_tree_beans.insert(0, [])
            
            elif tree.is_empty:
                tab_name = unicode(path[path.rfind("/") + 1:])
                vbox = gtk.VBox()
                label = gtk.Label(tab_name + " ")
                label.set_angle(90)
                if FC().tab_close_element:
                    vbox.pack_start(self.controls.tablib.button(tree.scroll), False, False)
                vbox.pack_end(label, False, False)
                event = self.controls.notetabs.to_eventbox(vbox, tree)
                event = self.controls.tablib.tab_menu_creator(event, tree.scroll)
                event.connect("button-press-event", self.controls.tablib.on_button_press) 
                self.controls.tablib.set_tab_label(tree.scroll, event)
                FC().tab_names[number_of_tab] = tab_name
                FC().music_paths[number_of_tab] = []
            
            for path in paths:
                if path in FC().music_paths[number_of_tab]:
                    pass
                else:
                    FC().music_paths[number_of_tab].append(path) 
                    self.controls.preferences.on_load()
                    LOG.info("New music paths", FC().music_paths[number_of_tab])
                    self.controls.update_music_tree(tree, number_of_tab)
            FC().save()
        elif response == gtk.RESPONSE_CANCEL:
            LOG.info('Closed, no files selected')
        chooser.destroy()
    
    def on_load(self):
        self.controls.load_music_tree()
        self.restore_selection(FC().nav_selected_paths)
    
    def on_save(self):
        pass
