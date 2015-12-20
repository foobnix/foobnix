'''
Created on Sep 29, 2010

@author: ivan
'''
import logging

from gi.repository import Gtk

from foobnix.gui.state import LoadSave
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click,\
    right_click_optimization_for_trees, is_empty_click
from foobnix.helpers.menu import Popup
from foobnix.helpers.dialog_entry import one_line_dialog
from foobnix.gui.model import FModel
from foobnix.gui.treeview.common_tree import CommonTreeControl
from foobnix.fc.fc import FC
from foobnix.fc.fc_cache import FCache
from foobnix.util.key_utils import KEY_DELETE, is_key


class VirtualTreeControl(CommonTreeControl, LoadSave):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)

        """column config"""
        column = Gtk.TreeViewColumn(_("Storage"), self.ellipsize_render, text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)

        self.tree_menu = Popup()

        self.configure_send_drag()
        self.configure_recive_drag()

        self.set_type_tree()

    def on_key_release(self, w, e):
        if is_key(e, KEY_DELETE):
            self.delete_selected()

    def on_drag_drop_finish(self):
        FCache().cache_virtual_tree_beans = self.get_all_beans()
        FC().save()

    def on_button_press(self, w, e):
        if is_empty_click(w, e):
            w.get_selection().unselect_all()
        if is_double_left_click(e):

            selected = self.get_selected_bean()
            beans = self.get_all_child_beans_by_selected()
            self.controls.notetabs._append_tab(selected.text, [selected] + beans, optimization=True)
            self.controls.play_first_file_in_playlist()

        if is_rigth_click(e):
                right_click_optimization_for_trees(w, e)
                self.tree_menu.clear()
                self.tree_menu.add_item(_("Add playlist"), "list-add", self.create_playlist, None)
                bean = self.get_selected_bean()
                if bean:
                    if bean.is_file:
                        self.tree_menu.add_item(_("Rename"), "accessories-text-editor", self.rename_selected, None)
                        self.tree_menu.add_item(_("Delete"), "edit-delete", self.delete_selected, None)
                    else:
                        self.tree_menu.add_item(_("Rename playlist"), "accessories-text-editor", self.rename_selected, None)
                        self.tree_menu.add_item(_("Delete playlist"), "edit-delete", self.delete_selected, None)
                #menu.add_item(_("Save as"), "document-save"_AS, None, None)
                #menu.add_item(_("Open as"), "folder-open", None, None)
                self.tree_menu.show(e)

    def create_playlist(self):
        name = one_line_dialog(_("Create new playlist"), self.controls.main_window, message_text1=_("Enter playlist name"))
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

    def rename_selected(self):
        bean = self.get_selected_bean()
        name = one_line_dialog(_("Rename Dialog"), self.controls.main_window,
                               entry_text=bean.text, message_text1=_("Enter new name"))
        if not name:
            return
        rows = self.find_rows_by_element(self.UUID, bean.UUID)
        if rows:
            rows[0][self.text[0]] = name

    def on_load(self):
        self.scroll.hide()
        self.restore_rows(FCache().cache_virtual_tree_beans)
        self.restore_expand(FC().virtual_expand_paths)
        self.restore_selection(FC().virtual_selected_paths)

        def set_expand_path(new_value):
            FC().virtual_expand_paths = new_value

        def set_selected_path(new_value):
            FC().virtual_selected_paths = new_value

        self.expand_updated(set_expand_path)
        self.selection_changed(set_selected_path)

    def on_quit(self):
        self.save_rows_from_tree(FCache().cache_virtual_tree_beans)

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
            if position == Gtk.TREE_VIEW_DROP_INTO_OR_BEFORE or position == Gtk.TREE_VIEW_DROP_INTO_OR_AFTER:
                self.model[path][self.font[0]] = 'bold'

        if self == ff_tree:
            ff_row_refs = [Gtk.TreeRowReference.new(ff_model, ff_path) for ff_path in ff_paths]

            def add_childs(treerow, new_iter):
                    for ch_row in treerow.iterchildren():
                        niter = model.append(new_iter, [col for col in ch_row])
                        add_childs(ch_row, niter)
            for treerow, ref in zip(treerows, ff_row_refs):
                row = [col for col in treerow]
                if drop_info:
                    if position == Gtk.TREE_VIEW_DROP_BEFORE:
                        new_iter = model.insert_before(None, iter, row)
                    elif (position == Gtk.TREE_VIEW_DROP_INTO_OR_BEFORE or
                          position == Gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
                        new_iter = model.append(iter, row)
                    else:
                        new_iter = model.insert_after(None, iter, row)
                        iter = model.iter_next(iter)
                else:
                    new_iter = model.append(None, row)
                treerow = model[ref.get_path()]     # reinitialize
                add_childs(treerow, new_iter)
            self.remove_replaced(ff_model, ff_row_refs)
        else:
            for treerow in treerows:
                row = [col for col in treerow]
                if drop_info:
                    if position == Gtk.TREE_VIEW_DROP_BEFORE:
                        new_iter = model.insert_before(None, iter, row)
                    elif (position == Gtk.TREE_VIEW_DROP_INTO_OR_BEFORE or
                          position == Gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
                        new_iter = model.append(iter, row)
                    else:
                        new_iter = model.insert_after(None, iter, row)
                        iter = model.iter_next(iter)
                else:
                    new_iter = model.append(None, row)
                if len(treerows) == 1 and treerow[self.font[0]] == 'bold':
                    while treerow.next and treerow.next[self.font[0]] != 'bold':
                        treerow = treerow.next
                        treerows.append(treerow)
                        drop_info = True
                        iter = new_iter
                        position = Gtk.TREE_VIEW_DROP_INTO_OR_AFTER

        self.stop_emission('drag-data-received')
