'''
Created on Sep 28, 2010

@author: ivan
'''

from gi.repository import Gtk

from foobnix.helpers.menu import Popup
from foobnix.gui.state import LoadSave
from foobnix.gui.model import FTreeModel
from foobnix.gui.treeview.common_tree import CommonTreeControl
from foobnix.util.mouse_utils import is_rigth_click, is_double_left_click, \
    is_left_click, right_click_optimization_for_trees, is_empty_click
from foobnix.util.const import FTYPE_NOT_UPDATE_INFO_PANEL, \
     DOWNLOAD_STATUS_ALL


class SimpleTreeControl(CommonTreeControl, LoadSave):
    def __init__(self, title_name, controls, head_visible=True):
        CommonTreeControl.__init__(self, controls)
        self.title_name = title_name

        self.set_reorderable(False)

        """column config"""
        column = Gtk.TreeViewColumn(title_name, self.ellipsize_render, text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.append_column(column)
        self.set_headers_visible(head_visible)

        self.configure_send_drag()

        self.set_type_plain()
        #self.populate_all([FModel("Madonna").add_is_file(True)])

        self.line_title = None

    def get_title(self):
        return self.title_name

    def on_button_press(self, w, e):
        if is_empty_click(w, e):
            w.get_selection().unselect_all()
        active = self.get_selected_bean()
        if active:
            active.type = FTYPE_NOT_UPDATE_INFO_PANEL
        else:
            return None

        if is_left_click(e):
            if active.get_status():
                if active.get_status() == DOWNLOAD_STATUS_ALL:
                    self.controls.dm.filter(None, FTreeModel().status[0])
                else:
                    self.controls.dm.filter(active.get_status(), FTreeModel().status[0])

        if is_double_left_click(e):
            self.controls.play(active)

        if is_rigth_click(e):
            right_click_optimization_for_trees(w, e)
            menu = Popup()
            menu.add_item(_('Play'), "media-playback-start", self.controls.play, active)
            menu.add_item(_('Copy to Search Line'), "edit-copy", self.controls.searchPanel.set_search_text, active.text)
            menu.show(e)

    def on_load(self):
        pass

    def on_save(self):
        pass

class SimpleListTreeControl(SimpleTreeControl):
    def __init__(self, title_name, controls, head_visible=True):
        SimpleTreeControl.__init__(self, title_name, controls, head_visible)

        self.left_click_func = None
        self.left_click_arg = None

        self.connect("cursor-changed", lambda * a:self.on_func())

    def set_left_click_func(self, func=None, arg=None):
        self.left_click_func = func
        self.left_click_arg = arg

    def on_func(self):
        if self.left_click_func and self.left_click_arg:
            self.left_click_func(self.left_click_arg)
        elif self.left_click_func:
            self.left_click_func()

    def on_button_press(self, w, e):
        if is_left_click(e):
            self.on_func()
        if is_double_left_click(e):
            pass

        if is_rigth_click(e):
            pass

