#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click, is_middle_click, is_left_click
from foobnix.regui.state import LoadSave
from foobnix.helpers.menu import Popup
from foobnix.util.fc import FC
import logging
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.const import LEFT_PERSPECTIVE_NAVIGATION

  
    
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
    
    def activate_perspective(self):
        FC().left_perspective = LEFT_PERSPECTIVE_NAVIGATION
    
    def on_button_press(self, w, e):
        
        if is_middle_click(e):
            self.add_to_tab(True)
            return

        if is_left_click(e):
            # on left click expand selected folders
            return
        
        if is_double_left_click(e):
            # on middle click play selected beans 
            self.add_to_tab()
            return
        
        if is_rigth_click(e):
            # on right click, show pop-up menu
            menu = Popup()
            menu.add_item(_("Add to current tab"), gtk.STOCK_ADD, lambda: self.add_to_tab(True), None)
            menu.add_item(_("Add to new tab"), gtk.STOCK_MEDIA_PLAY, self.add_to_tab, None)
            menu.add_separator()
            menu.add_item(_("Add folder"), gtk.STOCK_OPEN, self.add_folder, None)
            menu.add_separator()

            if FC().tabs_mode == "Multi":
                menu.add_item(_("Add folder in new tab"), gtk.STOCK_OPEN, lambda : self.add_folder(True), None)
                menu.add_item(_("Clear Music Tree"), gtk.STOCK_CLEAR, lambda : self.controls.tablib.clear_tree(self.scroll), None)
            menu.add_item(_("Update Music Tree"), gtk.STOCK_REFRESH, lambda: self.controls.tablib.on_update_music_tree(self.scroll), None)
                
            menu.show(e)

    def add_to_tab(self, current=False):
        paths = self.get_selected_bean_paths()
        to_model = self.controls.notetabs.get_current_tree().get_model().get_model()
        from_model = self.get_model()
        for i, path in enumerate(paths):
            from_iter = from_model.get_iter(path)
            row = self.get_row_from_model_iter(from_model, from_iter)
            
            if not i and not current:
                name = row[0]
                self.controls.notetabs._append_tab(name)
                to_model = self.controls.notetabs.get_current_tree().get_model().get_model()
            if self.add_m3u(from_model, from_iter, to_model, None, None): continue
            if from_model.iter_has_child(from_iter):
                new_iter = self.to_add_drug_item(to_model, None, None, None, True, row=row)
                from_ref = self.get_row_reference_from_iter(from_model, from_iter)
                self.iter_is_parent(from_ref, from_model, to_model, new_iter)
            else:
                new_iter = self.to_add_drug_item(to_model, None, None, None, row=row)
        
        self.controls.notetabs.get_active_tree().rebuild_as_plain()
        if not current:
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
                    logging.info("New music paths" + str(FC().music_paths[number_of_tab]))
                    self.controls.update_music_tree(tree, number_of_tab)
            FC().save()
        elif response == gtk.RESPONSE_CANCEL:
            logging.info('Closed, no files selected')
        chooser.destroy()       
        
    def on_load(self):
        self.controls.load_music_tree()
        self.restore_expand(FC().nav_expand_paths)
        self.restore_selection(FC().nav_selected_paths)
        
        def set_expand_path(new_value): FC().nav_expand_paths = new_value
        def set_selected_path(new_value): FC().nav_selected_paths = new_value
        self.expand_updated(set_expand_path)
        self.selection_changed(set_selected_path)
    
    def on_save(self):
        pass
