#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''

import os
import gtk
import logging
import gobject

from foobnix.fc.fc import FC
from foobnix.fc.fc_cache import FCache
from foobnix.regui.model import FModel
from foobnix.helpers.menu import Popup
from foobnix.regui.state import LoadSave
from foobnix.util.const import LEFT_PERSPECTIVE_NAVIGATION
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.file_utils import open_in_filemanager, rename_file_on_disk,\
    delete_files_from_disk, create_folder_dialog
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click, is_left_click, \
    is_middle_click_release, is_middle_click
    
class NavigationTreeControl(CommonTreeControl, LoadSave):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        
        self.controls = controls
        
        self.set_headers_visible(True)
        self.set_headers_clickable(True)
                
        """column config"""
        self.column = gtk.TreeViewColumn("File", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        self._append_column(self.column, _("File"))
        
        def func(column, cell, model, iter, ext=False):
            data = model.get_value(iter, self.text[0])
            if not model.get_value(iter, self.path[0]): 
                cell.set_property('text', '')
                return
            if os.path.isfile(model.get_value(iter, self.path[0])):
                if ext:
                    cell.set_property('text', os.path.splitext(data)[1][1:])
                else:
                    cell.set_property('text', os.path.splitext(data)[0])
            else:
                if ext:
                    cell.set_property('text', '')
                
        self.name_column = gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        self.name_column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        for rend in self.name_column.get_cell_renderers():
            self.name_column.set_cell_data_func(rend, func, False)
        self._append_column(self.name_column, _("Name"))
               
        self.ext_column = gtk.TreeViewColumn("Ext", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        for rend in self.ext_column.get_cell_renderers():
            self.ext_column.set_cell_data_func(rend, func, True)
        self._append_column(self.ext_column, _("Ext"))
          
        self.configure_send_drag()
        self.configure_recive_drag()
        
        self.set_type_tree()
        self.is_empty = False
        self.connect("button-release-event", self.on_button_release)
        
        '''to force the ext_column to take the minimum size'''
        self.name_column.set_fixed_width(2000)
        def task(*a):
            self.on_click_header(None, None, on_start=True)
        gobject.idle_add(task)
        
        self.scroll.get_vscrollbar().connect('show', task)
        self.scroll.get_vscrollbar().connect('hide', task)
                
    def activate_perspective(self):
        FC().left_perspective = LEFT_PERSPECTIVE_NAVIGATION
    
    def on_button_release(self, w, e):
        if is_middle_click_release(e):
            # on left click add selected items to current tab
            """to select item under cursor"""
            try:
                path, col, cellx, celly = self.get_path_at_pos(int(e.x), int(e.y)) #@UnusedVariable
                self.get_selection().select_path(path)
            except TypeError:
                pass
            self.add_to_tab(True)
            return
        
        
    def on_button_press(self, w, e):
        if is_middle_click(e):
            """to avoid unselect all selected items"""
            self.stop_emission('button-press-event')
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
            menu.add_item(_("Append to playlist"), gtk.STOCK_ADD, lambda: self.add_to_tab(True), None)
            menu.add_item(_("Open in new playlist"), gtk.STOCK_MEDIA_PLAY, self.add_to_tab, None)
            menu.add_separator()
            menu.add_item(_("Add folder here"), gtk.STOCK_OPEN, self.add_folder, None)
            menu.add_separator()

            if FC().tabs_mode == "Multi":
                menu.add_item(_("Add folder in new tab"), gtk.STOCK_OPEN, lambda : self.add_folder(True), None)
                menu.add_item(_("Clear"), gtk.STOCK_CLEAR, lambda : self.controls.tabhelper.clear_tree(self.scroll), None)
            menu.add_item(_("Update"), gtk.STOCK_REFRESH, lambda: self.controls.tabhelper.on_update_music_tree(self.scroll), None)
            
            f_model, f_t_paths = self.get_selection().get_selected_rows()
            if f_t_paths:
                model = f_model.get_model()
                t_paths = [f_model.convert_child_path_to_path(f_t_path) for f_t_path in f_t_paths]
                row = model[t_paths[0]]
                paths = [model[t_path][self.path[0]] for t_path in t_paths]
                row_refs = [gtk.TreeRowReference(model, t_path) for t_path in t_paths]
                menu.add_separator()
                menu.add_item(_("Open in file manager"), None, open_in_filemanager, self.get_selected_bean().path)
                menu.add_item(_("Create folder"), None, self.create_folder, (model, f_t_paths[0], row))
                menu.add_item(_("Rename file (folder)"), None, self.rename_files, (row, self.path[0], self.text[0]))    
                menu.add_item(_("Delete file(s) / folder(s)"), None, self.delete_files, (row_refs, paths, self.get_iter_from_row_reference))
            
            menu.show(e)
    
    def _append_column(self, column, title):
        column.label = gtk.Label(title)
        column.label.show()
        column.set_widget(column.label)
        column.set_clickable(True)
        self.append_column(column)
        column.button = column.label.get_parent().get_parent().get_parent()
        column.button.connect("button-press-event", self.on_click_header)
        
    def rename_files(self, a):
        row, index_path, index_text = a
        if rename_file_on_disk(row, index_path, index_text):
            old_bean = self.get_selected_bean()
            beans = FCache().cache_music_tree_beans[self.controls.tabhelper.get_current_page()]
            for bean in beans:
                if old_bean == bean:
                    bean.path = row[index_path]
                    bean.text = row[index_text]
                    break
    
    def delete_files(self, a):
        row_refs, paths, get_iter_from_row_reference = a
        copy_paths = paths[:]
        if delete_files_from_disk(row_refs, paths, get_iter_from_row_reference):
            beans = FCache().cache_music_tree_beans[self.controls.tabhelper.get_current_page()]
            for bean in beans[:] :
                if bean.path in copy_paths:
                    beans.remove(bean)
    
    def create_folder(self, a):
        model, tree_path, row = a
        file_path = row[self.path[0]]
        new_folder_path = create_folder_dialog(file_path)
        if os.path.isfile(file_path):
            iter = model.get_iter(tree_path)
            parent = model.iter_parent(iter)
        elif os.path.isdir(file_path):
            parent = model.get_iter(tree_path)
        else:
            logging.error("So path doesn't exist")
        bean = FModel(os.path.basename(new_folder_path), new_folder_path).add_parent(row[self.level[0]]).add_is_file(False)
        bean.font = "bold"
        bean.visible = True
        row = self.get_row_from_bean(bean)
        model.prepend(parent, row)
        self.save_beans_from_tree()
                
    def add_to_tab(self, current=False):
        paths = self.get_selected_bean_paths()
        to_tree = self.controls.notetabs.get_current_tree()
        try:
            to_model = to_tree.get_model().get_model()
        except AttributeError:
            pass
        from_model = self.get_model()
        for i, path in enumerate(paths):
            from_iter = from_model.get_iter(path)
            row = self.get_row_from_model_iter(from_model, from_iter)
            
            if not i and not current:
                name = row[0]
                self.controls.notetabs._append_tab(name)
                to_tree = self.controls.notetabs.get_current_tree() # because to_tree has changed
                to_model = to_tree.get_model().get_model()
                
            if self.add_m3u(from_model, from_iter, to_tree, to_model, None, None): continue
            if from_model.iter_has_child(from_iter):
                new_iter = self.to_add_drag_item(to_tree, to_model, None, None, None, True, row=row)
                from_ref = self.get_row_reference_from_iter(from_model, from_iter)
                self.iter_is_parent(from_ref, from_model, to_tree, to_model, new_iter)
            else:
                new_iter = self.to_add_drag_item(to_tree, to_model, None, None, None, row=row)
                
        #self.controls.notetabs.get_current_tree().rebuild_as_plain()
        to_tree.update_tracknumber()
        
        if not current:
            '''gobject because rebuild_as_plain use it too'''
            gobject.idle_add(self.controls.play_first_file_in_playlist)

    def add_folder(self, in_new_tab=False):
        chooser = gtk.FileChooserDialog(title=_("Choose directory with music"),
                                        action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_select_multiple(True)
        if FCache().last_music_path:
            chooser.set_current_folder(FCache().last_music_path)
        response = chooser.run()
        
        if response == gtk.RESPONSE_OK:
            paths = chooser.get_filenames()
            chooser.destroy()
            
            def task():
                path = paths[0]
                FCache().last_music_path = path[:path.rfind("/")]
                tree = self
                number_of_tab = self.controls.tabhelper.page_num(tree.scroll)
                          
                if in_new_tab:
                    tree = NavigationTreeControl(self.controls)
                    tab_name = unicode(path[path.rfind("/") + 1:])
                    self.controls.tabhelper._append_tab(tab_name, navig_tree=tree)
                    number_of_tab = self.controls.tabhelper.get_current_page()
                    FCache().music_paths.insert(0, [])
                    FCache().tab_names.insert(0, tab_name)
                    FCache().cache_music_tree_beans.insert(0, [])
                
                elif tree.is_empty:
                    tab_name = unicode(path[path.rfind("/") + 1:])
                    vbox = gtk.VBox()
                    label = gtk.Label(tab_name + " ")
                    label.set_angle(90)
                    if FC().tab_close_element:
                        vbox.pack_start(self.controls.tabhelper.button(tree.scroll), False, False)
                    vbox.pack_end(label, False, False)
                    event = self.controls.notetabs.to_eventbox(vbox, tree)
                    event = self.controls.tabhelper.tab_menu_creator(event, tree.scroll)
                    event.connect("button-press-event", self.controls.tabhelper.on_button_press) 
                    self.controls.tabhelper.set_tab_label(tree.scroll, event)
                    FCache().tab_names[number_of_tab] = tab_name
                    FCache().music_paths[number_of_tab] = []
                
                for path in paths:
                    if path in FCache().music_paths[number_of_tab]:
                        pass
                    else:
                        FCache().music_paths[number_of_tab].append(path) 
                        self.controls.preferences.on_load()
                        logging.info("New music paths" + str(FCache().music_paths[number_of_tab]))
                self.controls.update_music_tree(tree, number_of_tab)
                FC().save()
            self.controls.in_thread.run_with_progressbar(task, with_lock=False)
            
        elif response == gtk.RESPONSE_CANCEL:
            logging.info('Closed, no files selected')
            chooser.destroy()       
    
    def normalize_columns_width(self):
        if not hasattr(self, 'ext_width') or not self.ext_width:
            self.ext_width = self.ext_column.get_width()
        
        increase = 0
        vscrollbar = self.scroll.get_vscrollbar()
        if not vscrollbar.get_property('visible'):
            increase += 3
            
        self.name_column.set_fixed_width(self.get_allocation().width - self.ext_width - increase)
    
    def on_click_header(self, w, e, on_start=False):
        def task(tree):
            if FC().show_full_filename:
                tree.column.set_visible(True)
                tree.name_column.set_visible(False)
                tree.ext_column.set_visible(False)
            else:
                tree.column.set_visible(False)
                tree.name_column.set_visible(True)
                tree.ext_column.set_visible(True)
        
        if not on_start:
            FC().show_full_filename = not FC().show_full_filename
            for page in xrange(self.controls.tabhelper.get_n_pages()):
                tab_content = self.controls.tabhelper.get_nth_page(page)
                tree = tab_content.get_child()
                task(tree)
        else:
            task(self)
            self.normalize_columns_width()
        
    def on_load(self):
        self.controls.load_music_tree()
        self.restore_expand(FC().nav_expand_paths)
        self.restore_selection(FC().nav_selected_paths)
        
        def set_expand_path(new_value): 
            FC().nav_expand_paths = new_value
            
        def set_selected_path(new_value): 
            FC().nav_selected_paths = new_value
            
        self.expand_updated(set_expand_path)
        self.selection_changed(set_selected_path)
        
        """tab choose"""
        if FC().tabs_mode == "Single":
            self.controls.tabhelper.set_show_tabs(False)
        
    def on_save(self):
        pass
