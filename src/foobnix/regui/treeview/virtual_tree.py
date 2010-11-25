'''
Created on Sep 29, 2010

@author: ivan
'''
from foobnix.regui.state import LoadSave
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click
import gtk
from foobnix.helpers.menu import Popup
from foobnix.helpers.dialog_entry import one_line_dialog
from foobnix.regui.model import FModel
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.fc import FC
from foobnix.util.key_utils import KEY_DELETE, is_key
from foobnix.util.const import LEFT_PERSPECTIVE_VIRTUAL
class VirtualTreeControl(CommonTreeControl, LoadSave):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        
        """column config"""
        column = gtk.TreeViewColumn(_("Virtual PlayLists"), gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)
        
        self.configure_send_drug()
        self.configure_recive_drug()
        
        self.set_type_tree()
   
    def activate_perspective(self):
   
        FC().left_perspective = LEFT_PERSPECTIVE_VIRTUAL
    def on_key_release(self, w, e):
        if is_key(e, KEY_DELETE):
            self.delete_playlist()
    
    def on_drag_drop_finish(self):
        FC().cache_virtual_tree_beans = self.get_all_beans()
        FC().save()        
         
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            
            selected = self.get_selected_bean()
            beans = self.get_all_child_beans_by_selected()         
            self.controls.append_to_new_notebook(selected.text, [selected] + beans)
            
        if is_rigth_click(e): 
                menu = Popup()
                menu.add_item(_("Add playlist"), gtk.STOCK_ADD, self.create_playlist, None)
                menu.add_item(_("Rename playlist"), gtk.STOCK_EDIT, self.rename_playlist, None)
                menu.add_item(_("Delete playlist"), gtk.STOCK_DELETE, self.delete_playlist, None)
                #menu.add_item(_("Save as"), gtk.STOCK_SAVE_AS, None, None)
                #menu.add_item(_("Open as"), gtk.STOCK_OPEN, None, None)
                menu.show(e)
    
    def create_playlist(self):
        text = one_line_dialog("Create new playlist")
        bean = FModel(text).add_font("bold")
        self.append(bean)
              
    
    def delete_playlist(self):
        self.delete_selected()
    
    def rename_playlist(self):
        bean = self.get_selected_bean()
        text = one_line_dialog("Rename playlist", bean.text)
        if not text:
            return
        self.rename_selected(text)
  
        
    
    def on_load(self):
        self.scroll.hide()
        self.populate_all(FC().cache_virtual_tree_beans)
    
    def on_save(self):        
        FC().cache_virtual_tree_beans = self.get_all_beans()
        
