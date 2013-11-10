'''
Created on Oct 27, 2010

@author: ivan
'''
from foobnix.gui.treeview.simple_tree import SimpleTreeControl
from foobnix.util.const import DOWNLOAD_STATUS_ALL
from foobnix.gui.model import FTreeModel
from foobnix.util.mouse_utils import is_double_left_click, is_empty_click
class DMNavigationTreeControl(SimpleTreeControl):
    def __init__(self):
        SimpleTreeControl.__init__(self, None, None)
        self.dm_list = None
    
    def on_button_press(self, w, e):
        if is_empty_click(w,e):
            w.get_selection().unselect_all()
        if is_double_left_click(e):
            active = self.get_selected_bean()
            if active:
                if active.get_status() == DOWNLOAD_STATUS_ALL:
                    self.dm_list.filter_by_file(None, FTreeModel().status[0])
                else:
                    self.dm_list.filter_by_file(active.get_status(), FTreeModel().status[0])
    def use_filter(self):
        active = self.get_selected_bean()
        if active:
            if active.get_status() == DOWNLOAD_STATUS_ALL:
                self.dm_list.filter_by_file(None, FTreeModel().status[0])
            else:
                self.dm_list.filter_by_file(active.get_status(), FTreeModel().status[0])
    
    """statistics in {DOWNLOAD_TYPE:count}"""
    def update_statistics(self):
        statisctics = self.dm_list.get_status_statisctics()  
        all = self.get_all_beans()
        for bean in all:
            status = bean.get_status()
            num = 0
            if status in statisctics:
                num = statisctics[status]
            value = bean.artist + " (%s)" % num
            self.set_bean_column_value(bean, FTreeModel().text[0], value)
        
    def on_load(self):
        pass
    
    def on_save(self):
        pass
