'''
Created on Oct 27, 2010

@author: ivan
'''
from foobnix.regui.treeview.common_tree import CommonTreeControl
import gtk
from foobnix.util.const import DOWNLOAD_STATUS_ALL, DOWNLOAD_STATUS_ACTIVE, \
    DOWNLOAD_STATUS_LOCK
from foobnix.regui.model import FTreeModel
from foobnix.util.mouse_utils import is_rigth_click
from foobnix.util.file_utils import open_in_filemanager
import logging
from foobnix.fc.fc import FC
from foobnix.helpers.menu import Popup

class DownloadManagerTreeControl(CommonTreeControl):
    def __init__(self, navigation):
        self.navigation = navigation
        CommonTreeControl.__init__(self, None)
        self.set_reorderable(False)
        self.set_headers_visible(True)

        """column config"""
        column = gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=self.text[0])
        column.set_resizable(True)
        self.append_column(column)
        
        """column config"""
        column = gtk.TreeViewColumn("Progress", gtk.CellRendererProgress(), text=self.persent[0], value=self.persent[0])
        column.set_resizable(True)
        self.append_column(column)
        
        """column config"""
        column = gtk.TreeViewColumn("Size", gtk.CellRendererText(), text=self.size[0])
        column.set_resizable(True)
        self.append_column(column)
        
        """status"""
        column = gtk.TreeViewColumn("Status", gtk.CellRendererText(), text=self.status[0])
        column.set_resizable(True)
        self.append_column(column)
        
        """column config"""
        column = gtk.TreeViewColumn("Path", gtk.CellRendererText(), text=self.save_to[0])
        column.set_resizable(True)
        column.set_expand(True)
        self.append_column(column)
        

        self.set_type_plain()
        
    def delete_all(self):
        self.clear()
    
    def delete_all_selected(self):
        self.delete_selected()
        
    def update_status_for_selected(self, status):
        beans = self.get_all_selected_beans()
        for bean in beans:
            self.set_bean_column_value(bean, FTreeModel().status[0], status)
        
    def update_status_for_all(self, status):
        beans = self.get_all_beans()
        for bean in beans:
            self.set_bean_column_value(bean, FTreeModel().status[0], status)
    
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
    
    def update_bean_info(self, bean):
        self.update_bean(bean)
        self.navigation.update_statistics()
        #self.navigation.use_filter()
    
    def on_button_press(self, w, e):
        logging.debug("on dm button release")
        if is_rigth_click(e):
            menu = Popup()
            try:            
                if self.get_selected_bean():
                    menu.add_item(_("Open in file manager"), None, open_in_filemanager, self.get_selected_bean().path)
                else:
                    menu.add_item(_("Open in file manager"), None, open_in_filemanager, FC().online_save_to_folder)
            except Exception, e:
                logging.error(e)
            menu.show(e)
    
    def get_status_statisctics(self):
        all = self.get_all_beans()
        results = {}
        results[DOWNLOAD_STATUS_ALL] = len(all)
        for bean in all:
            status = bean.get_status()
            if status in results:
                results[status] = results[status] + 1
            else:
                results[status] = 1
        return results
             
        
