'''
Created on Jan 27, 2011

@author: ivan
'''
from gi.repository import Gtk
from gi.repository import GObject
import logging

from foobnix.fc.fc import FC
from foobnix.fc.fc_base import FCBase
from foobnix.helpers.menu import Popup
from foobnix.gui.model import FModel, FDModel
from foobnix.util.mouse_utils import is_rigth_click,\
    right_click_optimization_for_trees, is_empty_click
from foobnix.util.const import LEFT_PERSPECTIVE_LASTFM
from foobnix.util.bean_utils import update_parent_for_beans
from foobnix.gui.treeview.common_tree import CommonTreeControl


class LastFmIntegrationControls(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        
        """column config"""
        column = Gtk.TreeViewColumn(_("Lasm.fm Integration ") + FCBase().lfm_login,
                                    Gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)

        self.tree_menu = Popup()
        
        self.configure_send_drag()
        self.configure_recive_drag()
        
        self.set_type_tree()

        self.services = {_("My recommendations"):   self.controls.lastfm_service.get_recommended_artists,
                         _("My loved tracks"):      self.controls.lastfm_service.get_loved_tracks,
                         _("My top tracks"):        self.controls.lastfm_service.get_top_tracks,
                         _("My recent tracks"):     self.controls.lastfm_service.get_recent_tracks,
                         _("My top artists"):       self.controls.lastfm_service.get_top_artists,
                         #_("My friends"):self.controls.lastfm_service.get_friends,
                         # #_("My neighbours"):self.controls.lastfm_service.get_neighbours
                         }

        for name in self.services:
            parent = FModel(name)
            bean = FDModel(_("loading...")).parent(parent).add_is_file(True)
            self.append(parent)
            self.append(bean)

    def activate_perspective(self):   
        FC().left_perspective = LEFT_PERSPECTIVE_LASTFM

    def on_button_press(self, w, e):
        if is_empty_click(w, e):
            w.get_selection().unselect_all()
        if is_rigth_click(e):
            right_click_optimization_for_trees(w, e)
            active = self.get_selected_bean()
            self.tree_menu.clear()
            self.tree_menu.add_item(_('Play'), Gtk.STOCK_MEDIA_PLAY, self.controls.play, active)
            self.tree_menu.add_item(_('Copy to Search Line'), Gtk.STOCK_COPY,
                                    self.controls.searchPanel.set_search_text, active.text)
            self.tree_menu.show(e)
    
    def on_bean_expanded(self, parent):
        logging.debug("expanded %s" % parent)

        def task():
            old_iters = self.get_child_iters_by_parent(self.model, self.get_iter_from_bean(parent))
            childs = self.services[u""+parent.text](FCBase().lfm_login, str(FC().search_limit))
            update_parent_for_beans(childs, parent)
            self.append_all(childs)
            GObject.idle_add(self.remove_iters, old_iters)
        self.controls.in_thread.run_with_progressbar(task)
