#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''

import os
import logging
import threading

from gi.repository import Gtk
from gi.repository import GLib

from foobnix.fc.fc import FC
from foobnix.fc.fc_cache import FCache
from foobnix.gui.model import FModel
from foobnix.helpers.menu import Popup
from foobnix.gui.state import LoadSave
from foobnix.gui.treeview.common_tree import CommonTreeControl
from foobnix.util.file_utils import open_in_filemanager, rename_file_on_disk,\
    delete_files_from_disk, create_folder_dialog, is_m3u
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click, is_left_click, \
    is_middle_click_release, is_middle_click, right_click_optimization_for_trees,\
    is_empty_click


class NavigationTreeControl(CommonTreeControl, LoadSave):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)

        self.controls = controls
        self.full_name = ""
        self.label = Gtk.Label.new(None)

        self.tree_menu = Popup()

        self.set_headers_visible(True)
        self.set_headers_clickable(True)

        """column config"""
        self.column = Gtk.TreeViewColumn("File", self.ellipsize_render, text=self.text[0], font=self.font[0])
        self._append_column(self.column, _("File"))

        def func(column, cell, model, iter, ext=False):
            try:
                data = model.get_value(iter, self.text[0])
            except TypeError:
                data = None
                pass
            if not model.get_value(iter, self.path[0]):
                cell.set_property('text', '')
                return
            if os.path.isfile(model.get_value(iter, self.path[0])):
                if data:
                    if ext:
                        cell.set_property('text', os.path.splitext(data)[1][1:])
                    else:
                        cell.set_property('text', os.path.splitext(data)[0])
            else:
                if ext:
                    cell.set_property('text', '')

        self.name_column = Gtk.TreeViewColumn("Name", self.ellipsize_render, text=self.text[0], font=self.font[0])
        self.name_column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        for rend in self.name_column.get_cells():
            self.name_column.set_cell_data_func(rend, func, False)
        self._append_column(self.name_column, _("Name"))

        self.ext_column = Gtk.TreeViewColumn("Ext", Gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        for rend in self.ext_column.get_cells():
            self.ext_column.set_cell_data_func(rend, func, True)
        self._append_column(self.ext_column, _("Ext"))

        self.configure_send_drag()
        self.configure_recive_drag()

        self.set_type_tree()

        self.connect("button-release-event", self.on_button_release)
        self.connect("drag-data-get", self.on_drag_data_get)
        '''to force the ext_column to take the minimum size'''
        self.name_column.set_fixed_width(2000)

        def task(*a):
            self.on_click_header(None, None, on_start=True)
        GLib.idle_add(task)

        self.scroll.get_vscrollbar().connect('show', task)
        self.scroll.get_vscrollbar().connect('hide', task)

    def on_button_release(self, w, e):
        if is_middle_click_release(e):
            # on left click add selected items to current tab
            """to select item under cursor"""
            try:
                path, col, cellx, celly = self.get_path_at_pos(int(e.x), int(e.y))  # @UnusedVariable
                self.get_selection().select_path(path)
            except TypeError:
                pass
            self.add_to_tab(True)
            return

    def on_button_press(self, w, e):
        if is_empty_click(w, e):
            w.get_selection().unselect_all()
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
            right_click_optimization_for_trees(w, e)
            tabhelper = self.controls.perspectives.get_perspective('fs').get_tabhelper()
            # on right click, show pop-up menu
            self.tree_menu.clear()
            self.tree_menu.add_item(_("Append to playlist"), "list-add", lambda: self.add_to_tab(True), None)
            self.tree_menu.add_item(_("Open in new playlist"), "list-add", self.add_to_tab, None)
            self.tree_menu.add_separator()
            self.tree_menu.add_item(_("Add folder here"), "folder-open", self.add_folder, None)
            self.tree_menu.add_separator()

            if FC().tabs_mode == "Multi":
                self.tree_menu.add_item(_("Add folder in new tab"), "folder-open", lambda: self.add_folder(True), None)
                self.tree_menu.add_item(_("Clear"), "edit-clear", lambda: tabhelper.clear_tree(self.scroll), None)
            self.tree_menu.add_item(_("Update"), "view-refresh", lambda: tabhelper.on_update_music_tree(self.scroll), None)

            f_model, f_t_paths = self.get_selection().get_selected_rows()
            if f_t_paths:
                model = f_model.get_model()
                t_paths = [f_model.convert_child_path_to_path(f_t_path) for f_t_path in f_t_paths]
                row = model[t_paths[0]]
                paths = [model[t_path][self.path[0]] for t_path in t_paths]
                row_refs = [Gtk.TreeRowReference.new(model, t_path) for t_path in t_paths]
                self.tree_menu.add_separator()
                self.tree_menu.add_item(_("Open in file manager"), "system-file-manager", open_in_filemanager, self.get_selected_bean().path)
                self.tree_menu.add_item(_("Create folder"), "folder-new", self.create_folder, (model, f_t_paths[0], row))
                self.tree_menu.add_item(_("Rename file (folder)"), "edit-find-replace", self.rename_files, (row, self.path[0], self.text[0]))
                self.tree_menu.add_item(_("Delete file(s) / folder(s)"), "edit-delete", self.delete_files, (row_refs, paths, self.get_iter_from_row_reference))

            self.tree_menu.show(e)

    def _append_column(self, column, title):
        column.label = Gtk.Label.new(title)
        column.label.show()
        column.set_widget(column.label)
        column.set_clickable(True)
        self.append_column(column)
        column.button = column.label.get_parent().get_parent().get_parent()
        column.button.connect("button-press-event", self.on_click_header)

    def rename_files(self, a):
        row, index_path, index_text = a
        if rename_file_on_disk(row, index_path, index_text):
            self.save_tree()

    def delete_files(self, a):
        row_refs, paths, get_iter_from_row_reference = a
        if delete_files_from_disk(row_refs, paths, get_iter_from_row_reference):
            self.delete_selected()
            self.save_tree()

    def create_folder(self, a):
        model, tree_path, row = a # @UnusedVariable
        file_path = row[self.path[0]]
        new_folder_path = create_folder_dialog(file_path)
        bean = FModel(os.path.basename(new_folder_path), new_folder_path).add_is_file(False)
        if os.path.isfile(file_path):
            bean.add_parent(row[self.parent_level[0]])
        elif os.path.isdir(file_path):
            bean.add_parent(row[self.level[0]])
        else:
            logging.error("So path doesn't exist")
        self.tree_append(bean)
        self.save_tree()

    def add_to_tab(self, current=False):
        paths = self.get_selected_bean_paths()
        to_tree = self.controls.notetabs.get_current_tree()
        try:
            to_model = to_tree.get_model().get_model()
        except AttributeError:
            current = False
            to_model = None
        from_model = self.get_model()

        def task(to_tree, to_model):
            treerows = [from_model[path] for path in paths]
            for i, treerow in enumerate(treerows):
                for k, ch_row in enumerate(treerow.iterchildren()):
                    treerows.insert(i+k+1, ch_row)

            #treerows = self.playlist_filter(treerows)
            if not current:
                name = treerows[0][0]
                if isinstance(name, str):
                    name = unicode(name, "utf-8")
                self.controls.notetabs._append_tab(name)
                to_tree = self.controls.notetabs.get_current_tree()     # because to_tree has changed
                to_model = to_tree.get_model().get_model()
            for i, treerow in enumerate(treerows):
                if is_m3u(treerow[self.path[0]]):
                    rows = to_tree.file_paths_to_rows([treerow[self.path[0]]])
                    if rows:
                        rows.reverse()
                        map(lambda row: treerows.insert(i + 1, row), rows)
                        continue
                to_model.append(None, [col for col in treerow])
            t = threading.Thread(target=to_tree.safe_fill_treerows)
            t.start()
            t.join()
            if not current:
                '''gobject because rebuild_as_plain use it too'''
                self.controls.play_first_file_in_playlist()
            self.controls.notetabs.on_save_tabs()
        task(to_tree, to_model)
        #self.controls.search_progress.background_spinner_wrapper(task, to_tree, to_model)

    def add_folder(self, in_new_tab=False):
        chooser = Gtk.FileChooserDialog(title=_("Choose directory with music"),
                                        action=Gtk.FileChooserAction.SELECT_FOLDER,
                                        buttons=(_("Open"), Gtk.ResponseType.OK))
        chooser.set_default_response(Gtk.ResponseType.OK)
        chooser.set_select_multiple(True)
        if FCache().last_music_path:
            chooser.set_current_folder(FCache().last_music_path)
        response = chooser.run()

        if response == Gtk.ResponseType.OK:
            paths = chooser.get_filenames()
            chooser.destroy()
            self.controls.main_window.present()

            def task():
                tabhelper = self.controls.perspectives.get_perspective('fs').get_tabhelper()
                path = paths[0]
                FCache().last_music_path = path[:path.rfind("/")]
                tree = self
                number_of_tab = tabhelper.page_num(tree.scroll)

                tab_name = path[path.rfind("/") + 1:]
                if isinstance(tab_name, str):
                    tab_name = unicode(tab_name, "utf-8")

                if in_new_tab:
                    tabhelper._append_tab(tab_name)
                    tree = tabhelper.get_current_tree()
                    number_of_tab = tabhelper.get_current_page()
                    FCache().music_paths.insert(0, [])
                    FCache().tab_names.insert(0, tab_name)
                    FCache().cache_music_tree_beans.insert(0, {})
                elif tree.is_empty():
                    vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
                    label = Gtk.Label.new(tab_name + " ")
                    label.set_angle(90)
                    if FC().tab_close_element:
                        vbox.pack_start(tabhelper.button(tree.scroll), False, False, 0)
                    vbox.pack_end(label, False, False, 0)
                    event = self.controls.notetabs.to_eventbox(vbox, tree)
                    event = tabhelper.tab_menu_creator(event, tree.scroll)
                    event.connect("button-press-event", tabhelper.on_button_press)
                    tabhelper.set_tab_label(tree.scroll, event)
                    FCache().tab_names[number_of_tab] = tab_name
                    FCache().music_paths[number_of_tab] = []

                for path in paths:
                    if path in FCache().music_paths[number_of_tab]:
                        pass
                    else:
                        FCache().music_paths[number_of_tab].append(path)
                        #self.controls.preferences.on_load()
                        logging.info("New music paths" + str(FCache().music_paths[number_of_tab]))
                self.controls.update_music_tree(tree, number_of_tab)

            #self.controls.in_thread.run_with_spinner(task, with_lock=False)
            self.controls.search_progress.background_spinner_wrapper(task)
        else:
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
            tabhelper = self.controls.perspectives.get_perspective('fs').get_tabhelper()
            for page in xrange(tabhelper.get_n_pages()):
                tab_content = tabhelper.get_nth_page(page)
                tree = tab_content.get_child()
                task(tree)
        else:
            task(self)
            self.normalize_columns_width()

    def on_load(self):
        #self.controls.load_music_tree()
        self.restore_expand(FC().nav_expand_paths)
        self.restore_selection(FC().nav_selected_paths)

        def set_expand_path(new_value):
            FC().nav_expand_paths = new_value

        def set_selected_path(new_value):
            FC().nav_selected_paths = new_value

        self.expand_updated(set_expand_path)
        self.selection_changed(set_selected_path)

    def on_save(self):
        pass

    def on_drag_data_get(self, source_tree, drag_context, selection, info, time):
        treeselection = source_tree.get_selection()
        ff_model, ff_paths = treeselection.get_selected_rows()
        iters = [ff_model.get_iter(ff_path) for ff_path in ff_paths]
        all_file_paths = ''
        for iter in iters:
            all_iters = self.get_list_of_iters_with_children(ff_model, iter)
            file_paths = ','.join([ff_model.get_value(iter, self.path[0]) for iter in all_iters])
            all_file_paths += file_paths

        selection.set(selection.get_target(), 0, all_file_paths)
        self.stop_emission('drag-data-get')

    def save_tree(self):
        page_num = self.controls.perspectives.get_perspective('fs').get_tabhelper().page_num(self.scroll)
        self.save_rows_from_tree(FCache().cache_music_tree_beans[page_num])