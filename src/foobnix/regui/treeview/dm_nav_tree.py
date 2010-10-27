'''
Created on Oct 27, 2010

@author: ivan
'''
from foobnix.regui.treeview.simple_tree import SimpleTreeControl
from foobnix.util.const import DOWNLOAD_STATUS_ALL
from foobnix.regui.model import FTreeModel
from foobnix.util.mouse_utils import is_double_left_click
class DMNavigationTreeControl(SimpleTreeControl):
    def __init__(self, title_name, controls):
        SimpleTreeControl.__init__(self, title_name, controls)
    
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            active = self.get_selected_bean()
            if active:
                if active.get_status() == DOWNLOAD_STATUS_ALL:
                    self.controls.dm.filter(None, FTreeModel().status[0])
                else:
                    self.controls.dm.filter(active.get_status(), FTreeModel().status[0])
    
    """statistics in {DOWNLOAD_TYPE:count}"""
    def update_statistics(self, statisctics):
        all = self.get_all_beans()
        for bean in all:
            status = bean.get_status()
            num = statisctics[status]
            value = bean.artist + " (%s)"%num
            self.set_bean_column_value(bean, FTreeModel().text[0], value)
        
    def on_load(self):
        pass
    
    def on_save(self):
        pass