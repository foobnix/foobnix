'''
Created on Sep 29, 2010

@author: ivan
'''
import gtk
import logging
import gobject

from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.fc.fc import FC
from foobnix.fc.fc_cache import FCache
from foobnix.regui.model import FModel
from foobnix.helpers.dialog_entry import two_line_dialog
from foobnix.helpers.menu import Popup
from foobnix.util.const import FTYPE_RADIO, LEFT_PERSPECTIVE_RADIO
from foobnix.regui.service.radio_service import RadioFolder



class RadioTreeControl(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        self.set_reorderable(False)
        
        """column config"""
        column = gtk.TreeViewColumn(_("Radio Stations"), gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)
        
        self.configure_send_drug()

        self.set_type_tree()
        self.is_lazy_load = False
    
    def activate_perspective(self):
        FC().left_perspective = LEFT_PERSPECTIVE_RADIO
    
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            selected = self.get_selected_bean()
            beans = self.get_all_child_beans_by_selected()  
            self.controls.notetabs._append_tab(selected.text, [selected] + beans, optimization=True)
            "run radio channel"
            self.controls.play_first_file_in_playlist()
            
        if is_rigth_click(e): 
            menu = Popup()
            menu.add_item(_("Add Station"), gtk.STOCK_ADD, self.on_add_station, None)
            menu.add_item(_("Delete Station"), gtk.STOCK_DELETE, self.on_delete_station, None)
            menu.add_item(_("Edit Radio"), gtk.STOCK_EDIT, self.on_edit_radio, None)
            menu.add_separator()
            menu.add_item(_("Reload radio folder"), gtk.STOCK_REFRESH, self.update_radio_tree, None)            
            menu.show(e)
    
    def on_edit_radio(self):
        bean = self.get_selected_bean()
        text = two_line_dialog(_("Change Radio Station name and path"), _("Url"), bean.text, bean.path)
        if not text[0] or not text[1]:
            return
        bean.add_text(text[0])
        bean.add_path(text[1])
        self.update_bean(bean)
    
    def on_add_station(self):
        name, url = two_line_dialog("Add New Radio Station", "Enter Name and URL", "", "http://")
        bean = FModel(name, url).add_is_file(True)
        self.append(bean)
    
    def on_delete_station(self):
        self.delete_selected()
    
    def update_radio_tree(self):
        self.controls.in_thread.run_with_progressbar(self._update_radio_tree)
        
    def _update_radio_tree(self):
        logging.info("in update radio")
        self.clear_tree()
        self.radio_folder = RadioFolder()
        files = self.radio_folder.get_radio_FPLs()    
        def task():    
            for fpl in files:
                parent = FModel(fpl.name).add_is_file(False)
                self.append(parent)
                for radio, urls in fpl.urls_dict.iteritems():
                    child = FModel(radio, urls[0]).parent(parent).add_type(FTYPE_RADIO)
                    self.append(child)
        
            FC().cache_radio_tree_beans = self.get_all_beans()
            self.is_radio_populated = True
        gobject.idle_add(task)            

    
    def lazy_load(self):
        if not self.is_lazy_load:
            logging.debug("radio Lazy loading")
            self.populate_all(FCache().cache_radio_tree_beans)
            if not FCache().cache_radio_tree_beans:
                logging.debug("populdate from file system")
                self.update_radio_tree()
            self.is_lazy_load = True 
        
    def on_quit(self):
        FCache().cache_radio_tree_beans = self.get_all_beans()