'''
Created on Jan 27, 2011

@author: ivan
'''

import gtk
import gobject
import logging

from foobnix.fc.fc import FC
from foobnix.helpers.menu import Popup
from foobnix.regui.model import FModel, FDModel
from foobnix.util.const import LEFT_PERSPECTIVE_VK
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.mouse_utils import is_rigth_click, is_double_left_click,\
    right_click_optimization_for_trees, is_empty_click


class VKIntegrationControls(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        
        """column config"""
        column = gtk.TreeViewColumn(_("VK Integration "), gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)
        
        self.configure_send_drag()
        self.configure_recive_drag()
        
        self.set_type_tree()
        
        self.lazy = False
        self.cache =[]
    
    def lazy_load(self):
        if not self.controls.vk_service.is_authorized():
            return
        if not self.lazy:
            self.controls.in_thread.run_with_progressbar(self._lazy_load)
    
    def _lazy_load(self):
        def get_users_by_uuid(uuidd):
            for user in self.controls.vk_service.get_result('getProfiles', 'uids=' + uuidd):
                logging.debug(user)
                name = user['first_name'] + " " + user['last_name']
            
                parent = FModel(name)
                parent.user_id = user['uid']
                bean = FDModel(_("loading...")).parent(parent).add_is_file(True)
                
                self.append(parent)        
                self.append(bean)
        
        get_users_by_uuid(FC().user_id)
        
        uids = self.controls.vk_service.get_result('friends.get', 'uid=' + FC().user_id)
        if uids:
            get_users_by_uuid(",".join(["%s" % i for i in uids]))
                    
        self.lazy = True
        
    def activate_perspective(self):   
        FC().left_perspective = LEFT_PERSPECTIVE_VK
    
    def on_button_press(self, w, e):
        if is_empty_click(w, e):
            w.get_selection().unselect_all()
        if is_rigth_click(e):
            right_click_optimization_for_trees(w, e)
            active = self.get_selected_bean()
            if active:
                menu = Popup()
                if isinstance(active, FModel) and active.path:
                    menu.add_item(_('Play'), gtk.STOCK_MEDIA_PLAY, self.controls.play, active)
                menu.add_item(_('Copy to Search Line'), gtk.STOCK_COPY, self.controls.searchPanel.set_search_text, active.text)            
                menu.show(e)
         
        if is_double_left_click(e):
            selected = self.get_selected_bean()
            if not selected:
                return

            def task():
                if selected.user_id not in self.cache:
                    beans = self.get_user_tracks_as_beans(selected.user_id)
                else:
                    beans = self.get_all_child_beans_by_selected()
                self.controls.notetabs._append_tab(selected.text, [selected] + beans, optimization=True)
                "run radio channel"
                self.controls.play_first_file_in_playlist()

            self.controls.in_thread.run_with_progressbar(task)
            
    def on_row_expanded(self, widget, iter, path):
        self.on_bean_expanded(iter)

    def get_user_tracks_as_beans(self, user_id):
        beans = []
        result = self.controls.vk_service.get_result('audio.get', "uid=" + user_id)
        if not result:
            beans = [FDModel(_("No results found")).add_is_file(True)]
        else:
            for line in result:
                bean = FModel(line['artist'] + ' - ' + line['title'])
                bean.aritst = line['artist']
                bean.title = line['title']
                bean.time = convert_seconds_to_text(line['duration'])
                bean.path = line['url']
                bean.aid = line['aid']
                bean.oid = line['owner_id']
                bean.is_file = True
                beans.append(bean)
        return beans

    def on_bean_expanded(self, parent_iter):
        logging.debug("expanded %s" % parent_iter)
        
        p_iter = self.get_model().convert_iter_to_child_iter(parent_iter)
        parent = self.get_bean_from_iter(p_iter)
        
        if parent.user_id in self.cache:
            return None
        
        self.cache.append(parent.user_id)
        
        old_iters = self.get_child_iters_by_parent(self.model, p_iter)

        def task():
            beans = self.get_user_tracks_as_beans(parent.user_id)
            for bean in beans:
                bean.parent(parent)
                row = self.get_row_from_bean(bean)
                self.model.append(p_iter, row)
            
            for rem in old_iters:
                self.model.remove(rem)     
                    
        def g_task():
            gobject.idle_add(task)

        self.controls.in_thread.run_with_progressbar(g_task)
