'''
Created on Sep 29, 2010

@author: ivan
'''

from __future__ import with_statement

import logging
import os.path
import thread

from gi.repository import Gtk

from foobnix.fc.fc_cache import FCache, CACHE_RADIO_FILE
from foobnix.helpers.dialog_entry import two_line_dialog, one_line_dialog
from foobnix.helpers.menu import Popup
from foobnix.gui.model import FModel, FTreeModel
from foobnix.gui.service.radio_service import RadioFolder
from foobnix.gui.treeview.common_tree import CommonTreeControl
from foobnix.util import idle_task
from foobnix.util.const import FTYPE_RADIO
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click,\
    right_click_optimization_for_trees, is_empty_click
from foobnix.util.key_utils import is_key, KEY_DELETE


class RadioTreeControl(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        self.set_reorderable(False)
        self.switcher_label = _("My channels")
        self.tree_menu = Popup()

        """column config"""
        column = Gtk.TreeViewColumn(_("Radio Stations"), self.ellipsize_render, text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)

        self.configure_send_drag()
        self.configure_recive_drag()
        self.set_type_tree()

    @idle_task
    def on_load(self):
        if FCache().cache_radio_tree_beans:
            self.restore_rows(FCache().cache_radio_tree_beans)
        else:
            self.update_radio_tree()

    def on_button_press(self, w, e):
        if is_double_left_click(e):
            selected = self.get_selected_bean()
            beans = self.get_all_child_beans_by_selected()
            self.controls.notetabs._append_tab(selected.text, [selected] + beans, optimization=True)
            "run radio channel"
            self.controls.play_first_file_in_playlist()

        if is_rigth_click(e):
            right_click_optimization_for_trees(w, e)

            self.tree_menu.clear()
            bean = self.get_selected_bean()
            if bean:
                if self.get_selected_bean().is_file:
                    self.tree_menu.add_item(_("Edit Station"), "accessories-text-editor", self.on_edit_radio, None)
                    self.tree_menu.add_item(_("Delete Station"), "edit-delete", self.delete_selected, None)
                else:
                    self.tree_menu.add_item(_("Rename Group"), "accessories-text-editor", self.on_rename_group, None)
                    self.tree_menu.add_item(_("Delete Group"), "edit-delete", self.delete_selected, None)
                self.tree_menu.add_separator()
            self.tree_menu.add_item(_("Reload radio folder"), "view-refresh", self.update_radio_tree, None)
            self.tree_menu.show(e)

    def on_edit_radio(self):
        bean = self.get_selected_bean()
        name, url = two_line_dialog(_("Edit Radio"),
                                    parent = self.controls.main_window,
                                    message_text1 = _("Enter new name and URL"),
                                    message_text2 = None,
                                    entry_text1=bean.text,
                                    entry_text2 = bean.path)
        if not name or not url:
            return
        bean.add_text(name)
        bean.add_path(url)

        rows = self.find_rows_by_element(self.UUID, bean.UUID)
        if rows:
            rows[0][self.text[0]] = name
            rows[0][self.path[0]] = url

    def on_rename_group(self):
        bean = self.get_selected_bean()
        name = one_line_dialog(_("Rename Group"), self.controls.main_window,
                               entry_text=bean.text, message_text1=_("Enter new group name"))
        if not name:
            return
        rows = self.find_rows_by_element(self.UUID, bean.UUID)
        if rows:
            rows[0][self.text[0]] = name

    def on_add_station(self):
        name, url = two_line_dialog(_("Add New Radio Station"),
                                    parent = self.controls.main_window,
                                    message_text1 = _("Enter station name and URL"),
                                    message_text2 = None,
                                    entry_text1 = None,
                                    entry_text2 = "http://")
        if not name or not url:
            return
        bean = self.get_selected_bean()
        new_bean = FModel(name, url).add_type(FTYPE_RADIO).add_is_file(True)
        if bean:
            if bean.is_file:
                new_bean.add_parent(bean.parent_level)
            else:
                new_bean.add_parent(bean.level)
        self.append(new_bean)

    def on_save(self):
        pass

    #def update_radio_tree(self):
    #    self.controls.in_thread.run_with_spinner(self._update_radio_tree)

    @idle_task
    def update_radio_tree(self):
        logging.info("in update radio")
        self.clear_tree()
        self.radio_folder = RadioFolder()
        files = self.radio_folder.get_radio_FPLs()
        for fpl in files:
            parent = FModel(fpl.name).add_is_file(False)
            self.append(parent)
            keys = fpl.urls_dict.keys()
            keys.sort()
            for radio in keys:
                child = FModel(radio, fpl.urls_dict[radio][0]).parent(parent).add_type(FTYPE_RADIO).add_is_file(True)
                self.append(child)

    def auto_add_user_station(self):
        if os.path.isfile(CACHE_RADIO_FILE) and os.path.getsize(CACHE_RADIO_FILE) > 0:
            with open(CACHE_RADIO_FILE, 'r') as f:
                list = f.readlines()
                parent_level_for_depth = {}
                previous = {"bean": None, "depth": 0, "name": '', "url": ''}
                for line in list:
                    depth = self.simbol_counter(line, '-')
                    try:
                        name = line[depth : line.index('#')]
                    except ValueError, e:
                        logging.warning('\'#\' ' + str(e) + ' in line \"' + line + '\"')
                        continue
                    url = line[line.index('#') + 1 : -1]
                    bean = FModel(name)
                    if url:
                        bean.add_is_file(True).add_path(url).add_type(FTYPE_RADIO)
                    if previous["depth"] < depth:
                        bean.add_parent(previous["bean"].level)
                    elif previous["depth"] > depth:
                        bean.add_parent(parent_level_for_depth[depth])
                    else:
                        if previous["bean"]:
                            bean.add_parent(previous["bean"].parent_level)

                    self.append(bean)
                    parent_level_for_depth[depth] = bean.parent_level
                    previous = {"bean": bean, "depth": depth, "name": name, "url": url}

    def simbol_counter(self, line, simbol):
        counter = 0
        for letter in line:
            if letter == simbol:
                counter += 1
            else:
                break
        return counter

    def lazy_load(self):
        def task():
            logging.debug("radio Lazy loading")
            if FCache().cache_radio_tree_beans:
                self.populate_all(FCache().cache_radio_tree_beans)
            else:
                self.update_radio_tree()
            self.is_radio_populated = True
        thread.start_new_thread(task, ())

    def on_quit(self):
        self.save_rows_from_tree(FCache().cache_radio_tree_beans)


class MyRadioTreeControl(RadioTreeControl):
    def __init__(self, controls):
        RadioTreeControl.__init__(self, controls)
        self.switcher_label = _("Autogenerated channels")

    def on_load(self):
        self.auto_add_user_station()

    def on_button_press(self, w, e):
        if is_empty_click(w, e):
            w.get_selection().unselect_all()

        if is_double_left_click(e):
            selected = self.get_selected_bean()
            beans = self.get_all_child_beans_by_selected()
            self.controls.notetabs._append_tab(selected.text, [selected] + beans, optimization=True)
            "run radio channel"
            self.controls.play_first_file_in_playlist()

        if is_rigth_click(e):
            right_click_optimization_for_trees(w, e)

            self.tree_menu.clear()
            self.tree_menu.add_item(_("Add Station"), "list-add", self.on_add_station, None)
            self.tree_menu.add_item(_("Create Group"), "list-add", self.create_new_group, None)
            bean = self.get_selected_bean()
            if bean:
                if self.get_selected_bean().is_file:
                    self.tree_menu.add_item(_("Edit Station"), "accessories-text-editor", self.on_edit_radio, None)
                    self.tree_menu.add_item(_("Delete Station"), "edit-delete", self.delete_selected, None)
                else:
                    self.tree_menu.add_item(_("Rename Group"), "accessories-text-editor", self.on_rename_group, None)
                    self.tree_menu.add_item(_("Delete Group"), "edit-delete", self.delete_selected, None)
            self.tree_menu.show(e)

    def on_key_release(self, w, e):
        if is_key(e, KEY_DELETE):
            self.delete_selected()

    def create_new_group(self):
        name = one_line_dialog(_("Create Group"), self.controls.main_window, message_text1=_("Enter group name"))
        if not name:
            return
        bean = self.get_selected_bean()
        folder_bean = FModel(name)
        if bean:
            if bean.is_file:
                folder_bean.add_parent(bean.parent_level)
            else:
                folder_bean.add_parent(bean.level)
        self.append(folder_bean)
        '''
        #another method without sorting
        selected = self.get_dest_row_at_pos(x, y)
        if selected:
            m, paths = selected
            iter = self.get_iter(paths[0])
            treerow = self[paths[0]]
            row = [col for col in treerow]
            if self.get_value(iter, self.is_file[0]):
                self.insert_after(None, iter, row)
            else:
                self.append(iter, row)
        else:
            self.append(None, row)
        '''

    def on_quit(self):

        with open(CACHE_RADIO_FILE, 'w') as f:
            def task(row):
                iter = row.iter
                level = self.model.iter_depth(iter)
                text = self.model.get_value(iter, FTreeModel().text[0])
                path = self.model.get_value(iter, FTreeModel().path[0])
                if not path:
                    path = ""
                f.write(level * '-' + text + '#' + path + '\n')
                if row.iterchildren():
                    for child_row in row.iterchildren():
                        task(child_row)

            for row in self.model:
                task(row)

    def on_drag_data_received(self, treeview, context, x, y, selection, info, timestamp):
        logging.debug('Storage on_drag_data_received')
        model = self.get_model().get_model()
        drop_info = self.get_dest_row_at_pos(x, y)

        # ff - from_filter
        ff_tree = Gtk.drag_get_source_widget(context)
        ff_model, ff_paths = ff_tree.get_selection().get_selected_rows()
        treerows = [ff_model[ff_path] for ff_path in ff_paths]
        if drop_info:
            path, position = drop_info
            iter = model.get_iter(path)

        if self == ff_tree:
            ff_row_refs = [Gtk.TreeRowReference.new(ff_model, ff_path) for ff_path in ff_paths]

            def add_childs(treerow, new_iter):
                    for ch_row in treerow.iterchildren():
                        niter = model.append(new_iter, [col for col in ch_row])
                        add_childs(ch_row, niter)
            for treerow, ref in zip(treerows, ff_row_refs):
                row = [col for col in treerow]
                if drop_info:
                    if position == Gtk.TreeViewDropPosition.BEFORE:
                        new_iter = model.insert_before(None, iter, row)
                    elif (position == Gtk.TreeViewDropPosition.INTO_OR_BEFORE or
                          position == Gtk.TreeViewDropPosition.INTO_OR_AFTER):
                        if model.get_value(iter, self.is_file[0]):
                            new_iter = model.insert_after(None, iter, row)
                            iter = model.iter_next(iter)
                        else:
                            new_iter = model.append(iter, row)
                    else:
                        new_iter = model.insert_after(None, iter, row)
                        iter = model.iter_next(iter)
                else:
                    new_iter = model.append(None, row)
                treerow = model[ref.get_path()]     # reinitialize
                add_childs(treerow, new_iter)
            self.remove_replaced(ff_model, ff_row_refs)

        self.stop_emission('drag-data-received')