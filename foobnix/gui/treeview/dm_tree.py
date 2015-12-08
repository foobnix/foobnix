'''
Created on Oct 27, 2010

@author: ivan
'''

import logging

from gi.repository import Gtk

from foobnix.util import idle_task
from foobnix.fc.fc import FC
from foobnix.helpers.menu import Popup
from foobnix.gui.model import FTreeModel
from foobnix.util.file_utils import open_in_filemanager
from foobnix.gui.treeview.common_tree import CommonTreeControl
from foobnix.util.const import DOWNLOAD_STATUS_ALL, DOWNLOAD_STATUS_ACTIVE, \
    DOWNLOAD_STATUS_LOCK
from foobnix.util.mouse_utils import is_rigth_click,\
    right_click_optimization_for_trees, is_empty_click


class DownloadManagerTreeControl(CommonTreeControl):
    def __init__(self, navigation):
        self.navigation = navigation
        CommonTreeControl.__init__(self, None)
        self.set_reorderable(False)
        self.set_headers_visible(True)

        self.tree_menu = Popup()

        """column config"""
        column = Gtk.TreeViewColumn(_("Name"), self.ellipsize_render, text=self.text[0])
        column.set_resizable(True)
        self.append_column(column)

        """column config"""
        column = Gtk.TreeViewColumn(_("Progress"), Gtk.CellRendererProgress(), text=self.persent[0], value=self.persent[0])
        column.set_resizable(True)
        self.append_column(column)

        """column config"""
        column = Gtk.TreeViewColumn(_("Size"), self.ellipsize_render, text=self.size[0])
        column.set_resizable(True)
        self.append_column(column)

        """status"""
        column = Gtk.TreeViewColumn(_("Status"), self.ellipsize_render, text=self.status[0])
        column.set_resizable(True)
        self.append_column(column)

        """column config"""
        column = Gtk.TreeViewColumn(_("Path"), self.ellipsize_render, text=self.save_to[0])
        column.set_resizable(True)
        column.set_expand(True)
        self.append_column(column)

        self.set_type_plain()

    @idle_task
    def delete_all(self):
        self.clear()

    @idle_task
    def delete_all_selected(self):
        self.delete_selected()

    @idle_task
    def update_status_for_selected(self, status):
        beans = self.get_all_selected_beans()
        for bean in beans:
            self.set_bean_column_value(bean, FTreeModel().status[0], status)

    @idle_task
    def update_status_for_all(self, status):
        beans = self.get_all_beans()
        for bean in beans:
            self.set_bean_column_value(bean, FTreeModel().status[0], status)

    @idle_task
    def update_status_for_beans(self, beans, status):
        for bean in beans:
            self.set_bean_column_value(bean, FTreeModel().status[0], status)

    def get_next_bean_to_dowload(self):
        all = self.get_all_beans()
        if not all:
            return None
        for bean in all:
            if bean.get_status() == DOWNLOAD_STATUS_ACTIVE:
                self.set_bean_column_value(bean, FTreeModel().status[0], DOWNLOAD_STATUS_LOCK)
                return bean

    @idle_task
    def update_bean_info(self, bean):
        self.update_bean(bean)
        self.navigation.update_statistics()
        #self.navigation.use_filter()

    def on_button_press(self, w, e):
        logging.debug("on dm button press")
        if is_empty_click(w, e):
            w.get_selection().unselect_all()
        if is_rigth_click(e):
            right_click_optimization_for_trees(w, e)
            try:
                self.tree_menu.clear()
                if self.get_selected_bean():
                    self.tree_menu.add_item(_("Open in file manager"), None, open_in_filemanager, self.get_selected_bean().path)
                else:
                    self.tree_menu.add_item(_("Open in file manager"), None, open_in_filemanager, FC().online_save_to_folder)
                self.tree_menu.show(e)
            except Exception, e:
                logging.error(e)

    def get_status_statisctics(self):
        all_beans = self.get_all_beans()
        if not all_beans:
            return {}
        results = {DOWNLOAD_STATUS_ALL: len(all_beans)}
        for bean in all_beans:
            status = bean.get_status()
            if status in results:
                results[status] += 1
            else:
                results[status] = 1
        return results
