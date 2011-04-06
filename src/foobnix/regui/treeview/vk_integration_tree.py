'''
Created on Jan 27, 2011

@author: ivan
'''

import gtk
import gobject
import logging

from foobnix.fc.fc import FC
from foobnix.fc.fc_base import FCBase
from foobnix.helpers.menu import Popup
from foobnix.regui.model import FModel, FDModel
from foobnix.util.const import LEFT_PERSPECTIVE_VK
from foobnix.util.bean_utils import update_parent_for_beans
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.mouse_utils import is_rigth_click, is_double_left_click


class VKIntegrationControls(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        
        """column config"""
        column = gtk.TreeViewColumn(_("VK Integration ") + FCBase().vk_login, gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)
        
        self.configure_send_drag()
        self.configure_recive_drag()
        
        self.set_type_tree()
        
        self.lazy = False
        self.cache =[]
    
    def lazy_load(self):
        self.controls.in_thread.run_with_progressbar(self._lazy_load)
    
    def _lazy_load(self):
        if self.lazy or not hasattr(self.controls.vk_service,"api"):
            return True
        
        def get_users_by_uuid(uuidd):
            for user in self.controls.vk_service.api.get('getProfiles',uids=uuidd):
                logging.debug(user)
                name =  user['first_name']+ " "+ user['last_name']
            
                parent = FModel(name)
                parent.user_id = user['uid']
                bean = FDModel(_("loading...")).parent(parent)
                
                self.append(parent)        
                self.append(bean)
        
        get_users_by_uuid(self.controls.vk_service.api.my_user_id)
        
        uids = self.controls.vk_service.api.get('friends.get')
        if uids:
            get_users_by_uuid(uids)
        
        self.lazy = True
        
    def activate_perspective(self):   
        FC().left_perspective = LEFT_PERSPECTIVE_VK
    
    def on_button_press(self, w, e):
        active = self.get_selected_bean()
        if active and is_rigth_click(e):
            menu = Popup()
            menu.add_item(_('Play'), gtk.STOCK_MEDIA_PLAY, self.controls.play, active)
            menu.add_item(_('Copy to Search Line'), gtk.STOCK_COPY, self.controls.searchPanel.set_search_text, active.text)            
            menu.show(e)
         
        
        if is_double_left_click(e):
            selected = self.get_selected_bean()
            beans = self.get_all_child_beans_by_selected()  
            self.controls.notetabs._append_tab(selected.text, [selected] + beans, optimization=True)
            "run radio channel"
            self.controls.play_first_file_in_playlist()

    def on_bean_expanded(self, parent):
        logging.debug("expanded %s" % parent)
        if parent.user_id in self.cache:
            return None
        
        def task():
            old_iters = self.get_child_iters_by_parent(self.model, self.get_iter_from_bean(parent));
            childs = []
            for line in self.controls.vk_service.api.get('audio.get',uid=parent.user_id):
                bean = FModel(line['artist']+' - '+line['title'])
                bean.aritst = line['artist']
                bean.title = line['title']
                bean.time = convert_seconds_to_text(line['duration'])
                bean.path = line['url']
                childs.append(bean)
                        
            update_parent_for_beans(childs, parent)
            
            self.append_all(childs)            
            gobject.idle_add(self.remove_iters,old_iters)        
            
            #gobject.idle_add(sub_task)
        #task()
        self.controls.in_thread.run_with_progressbar(task)
