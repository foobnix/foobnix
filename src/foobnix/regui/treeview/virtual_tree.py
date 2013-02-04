'''
Created on Sep 29, 2010

@author: ivan
'''
import gtk

from foobnix.regui.state import LoadSave
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click,\
    right_click_optimization_for_trees, is_empty_click
from foobnix.helpers.menu import Popup
from foobnix.helpers.dialog_entry import one_line_dialog
from foobnix.regui.model import FModel
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.fc.fc import FC
from foobnix.fc.fc_cache import FCache
from foobnix.util.key_utils import KEY_DELETE, is_key
from foobnix.util.const import LEFT_PERSPECTIVE_VIRTUAL

class VirtualTreeControl(CommonTreeControl, LoadSave):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        
        """column config"""
        column = gtk.TreeViewColumn(_("Storage"), gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)
        
        self.configure_send_drag()
        self.configure_recive_drag()
        
        self.set_type_tree()
   
    def activate_perspective(self):
   
        FC().left_perspective = LEFT_PERSPECTIVE_VIRTUAL
    
    def on_key_release(self, w, e):
        if is_key(e, KEY_DELETE):
            self.delete_selected()
    
    def on_drag_drop_finish(self):
        FCache().cache_virtual_tree_beans = self.get_all_beans()
        FC().save()        
        
    def on_button_press(self, w, e):
        if is_empty_click(w, e):
            w.get_selection().unselect_all()
        if is_double_left_click(e):
            
            selected = self.get_selected_bean()
            beans = self.get_all_child_beans_by_selected()         
            self.controls.notetabs._append_tab(selected.text, [selected] + beans, optimization=True)
            self.controls.play_first_file_in_playlist()
            
        if is_rigth_click(e): 
                right_click_optimization_for_trees(w, e)
                menu = Popup()
                menu.add_item(_("Add playlist"), gtk.STOCK_ADD, self.create_playlist, None)
                bean = self.get_selected_bean()
                if bean:
                    if bean.is_file:
                        menu.add_item(_("Rename"), gtk.STOCK_EDIT, self.rename_selected, None)
                        menu.add_item(_("Delete"), gtk.STOCK_DELETE, self.delete_selected, None)
                    else:
                        menu.add_item(_("Rename playlist"), gtk.STOCK_EDIT, self.rename_selected, None)
                        menu.add_item(_("Delete playlist"), gtk.STOCK_DELETE, self.delete_selected, None)
                #menu.add_item(_("Save as"), gtk.STOCK_SAVE_AS, None, None)
                #menu.add_item(_("Open as"), gtk.STOCK_OPEN, None, None)
                menu.show(e)
    
    def create_playlist(self):
        name = one_line_dialog(_("Create new playlist"), self.controls.main_window, message_text1=_("Enter playlist name"))
        if not name:
            return
        bean = self.get_selected_bean()
        folder_bean = FModel(name)
        if bean:
            if bean.is_file:
                folder_bean.add_parent(bean.parent_level)
            else:
                folder_bean.add_parent(bean.level)
        self.append(folder_bean)      
    
    def rename_selected(self):
        bean = self.get_selected_bean()
        name = one_line_dialog(_("Rename Dialog"), self.controls.main_window,
                               entry_text=bean.text, message_text1=_("Enter new name"))
        if not name:
            return
        rows = self.find_rows_by_element(self.UUID, bean.UUID)
        if rows:
            rows[0][self.text[0]] = name
    
    def on_load(self):
        self.scroll.hide()
        self.populate_all(FCache().cache_virtual_tree_beans)
        self.restore_expand(FC().virtual_expand_paths)
        self.restore_selection(FC().virtual_selected_paths)
        
        def set_expand_path(new_value): 
            FC().virtual_expand_paths = new_value
            
        def set_selected_path(new_value):             
            FC().virtual_selected_paths = new_value
            
        self.expand_updated(set_expand_path)
        self.selection_changed(set_selected_path)
    
    def on_quit(self):
        FCache().cache_virtual_tree_beans = self.get_all_beans()
        
