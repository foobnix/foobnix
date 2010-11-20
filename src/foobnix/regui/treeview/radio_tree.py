'''
Created on Sep 29, 2010

@author: ivan
'''
from foobnix.regui.state import LoadSave
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click
import gtk
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.fc import FC
from foobnix.radio.radios import RadioFolder
from foobnix.regui.model import FModel
from foobnix.helpers.dialog_entry import one_line_dialog, two_line_dialog
from foobnix.helpers.menu import Popup
from foobnix.util.const import FTYPE_RADIO, LEFT_PERSPECTIVE_RADIO
class RadioTreeControl(CommonTreeControl, LoadSave):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        self.set_reorderable(False)
        
        """column config"""
        column = gtk.TreeViewColumn("Radio Library", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)
        
        self.configure_send_drug()

        self.set_type_tree()
    
    def activate_perspective(self):
        FC().left_perspective = LEFT_PERSPECTIVE_RADIO
    
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            selected = self.get_selected_bean()
            print "selected", selected
            beans = self.get_all_child_beans_by_selected()  
            self.controls.append_to_new_notebook(selected.text, [selected] + beans)
        if is_rigth_click(e): 
            menu = Popup()
            menu.add_item(_("Add Station"), gtk.STOCK_ADD, self.on_add_station, None)
            menu.add_item(_("Delete Station"), gtk.STOCK_DELETE, self.on_delete_station, None)
            menu.add_item(_("Rename Station"), gtk.STOCK_EDIT, self.on_raname, None)
            menu.add_separator()
            menu.add_item(_("Restore Defaults"), gtk.STOCK_REFRESH, self.update_radio_tree, None)            
            menu.show(e)
    
    def on_raname(self):
        bean = self.get_selected_bean()
        text = one_line_dialog("Rename Radio", bean.text)
        if not text:
            return
        self.rename_selected(text)
    
    def on_add_station(self):
        name, url = two_line_dialog("Add New Radio Station", "Enter Name and URL", "", "http://")
        bean = FModel(name, url).add_is_file(True)
        self.append(bean)
    
    def on_delete_station(self):
        self.delete_selected()
    
    def update_radio_tree(self):        
        self.clear()
        self.radio_folder = RadioFolder()
        files = self.radio_folder.get_radio_FPLs()        
        for fpl in files:
            parent = FModel(fpl.name).add_is_file(False)
            self.append(parent)
            for radio, urls in fpl.urls_dict.iteritems():
                child = FModel(radio, urls[0]).parent(parent).add_type(FTYPE_RADIO)
                self.append(child)
        self.is_radio_populated = True            
    
    def on_load(self):
        self.scroll.hide()
        self.populate_all(FC().cache_radio_tree_beans)
        if not FC().cache_radio_tree_beans:
            self.update_radio_tree()
        
    
    def on_save(self):        
        FC().cache_radio_tree_beans = self.get_all_beans()
        
