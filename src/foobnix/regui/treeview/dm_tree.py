'''
Created on Oct 27, 2010

@author: ivan
'''
from foobnix.regui.treeview.common_tree import CommonTreeControl
import gtk
from foobnix.util.const import DOWNLOAD_STATUS_ALL, DOWNLOAD_STATUS_ACTIVE,\
    DOWNLOAD_STATUS_DOWNLOADING, DOWNLOAD_STATUS_LOCK
from foobnix.regui.model import FTreeModel
class DownloadManagerTreeControl(CommonTreeControl):
    def __init__(self, navigation):
        self.navigation = navigation
        CommonTreeControl.__init__(self, None)
        self.set_reorderable(False)
        self.set_headers_visible(True)
        
        """column config"""
        #column = gtk.TreeViewColumn("N", gtk.CellRendererText(), text=self.tracknumber[0], font=self.font[0])
        #column.set_resizable(True)
        #self.append_column(column)
        
        
        """column config"""
        column = gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=self.text[0])
        column.set_resizable(True)
        self.append_column(column)
        
        """column config"""
        column = gtk.TreeViewColumn("Path", gtk.CellRendererText(), text=self.save_to[0])
        column.set_resizable(True)
        column.set_expand(True)
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
        

        self.set_type_plain()
        
    def get_next_bean_to_dowload(self):
        all = self.get_all_beans()
        if not all:
            return None
        for bean in all:
            if bean.get_status() == DOWNLOAD_STATUS_ACTIVE:
                self.set_bean_column_value(bean, FTreeModel().status[0], DOWNLOAD_STATUS_LOCK)
                return bean
        
    
    def update_bean_info(self, bean):
        #gtk.gdk.threads_enter()     
        self.update_bean(bean)
        self.navigation.update_statistics()
        #self.navigation.use_filter()
        #gtk.gdk.threads_leave()
        
        
        
    
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
             
        