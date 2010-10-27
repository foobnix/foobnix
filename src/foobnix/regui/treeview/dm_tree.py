'''
Created on Oct 27, 2010

@author: ivan
'''
from foobnix.regui.treeview.common_tree import CommonTreeControl
import gtk
from foobnix.util.const import DOWNLOAD_STATUS_ALL
class DownloadManagerTreeControl(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        self.set_reorderable(False)
        self.set_headers_visible(True)
        
        """column config"""
        column = gtk.TreeViewColumn("N", gtk.CellRendererText(), text=self.tracknumber[0], font=self.font[0])
        column.set_resizable(True)
        self.append_column(column)
        
        """column config"""
        column = gtk.TreeViewColumn("Name", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.append_column(column)
        
        """column config"""
        column = gtk.TreeViewColumn("Path", gtk.CellRendererText(), text=self.save_to[0], font=self.font[0])
        column.set_resizable(True)
        column.set_expand(True)
        self.append_column(column)
        
        """column config"""
        column = gtk.TreeViewColumn("Progress", gtk.CellRendererText(), text=self.status[0], font=self.font[0])
        column.set_resizable(True)
        self.append_column(column)
        

        self.set_type_plain()
    
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
             
        