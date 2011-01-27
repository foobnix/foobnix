'''
Created on Jan 27, 2011

@author: ivan
'''
from foobnix.regui.treeview.common_tree import CommonTreeControl
import gtk
from foobnix.util.const import LEFT_PERSPECTIVE_LASTFM
from foobnix.util.fc import FC
from foobnix.regui.model import FModel
from foobnix.util.bean_utils import update_parent_for_beans

class LastFmIntegrationControls(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        
        """column config"""
        column = gtk.TreeViewColumn(_("Lasm.fm Integration"), gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.set_headers_visible(True)
        self.append_column(column)
        
        self.configure_send_drug()
        self.configure_recive_drug()
        
        self.set_type_tree()
               
        
    def activate_perspective(self):   
        FC().left_perspective = LEFT_PERSPECTIVE_LASTFM
        
    def update(self):
        self.controls.in_thread.run_with_progressbar(self._update)
        
    def _update(self):        
        self.clear_tree()
        parent = FModel("My loved tracks")
        self.append(parent)        
        childs = self.controls.lastfm_service.get_loved_tracks(FC().lfm_login)        
        update_parent_for_beans(childs, parent)        
        self.append_all(childs)
        
        
        parent = FModel("My Top tracks")
        self.append(parent)        
        childs = self.controls.lastfm_service.get_top_tracks(FC().lfm_login)        
        update_parent_for_beans(childs, parent)        
        self.append_all(childs)
        
        parent = FModel("My Recent tracks")
        self.append(parent)        
        childs = self.controls.lastfm_service.get_recent_tracks(FC().lfm_login)        
        update_parent_for_beans(childs, parent)        
        self.append_all(childs)
        
        parent = FModel("My top atrists")
        self.append(parent)        
        childs = self.controls.lastfm_service.get_top_artists(FC().lfm_login)        
        update_parent_for_beans(childs, parent)        
        self.append_all(childs)
        
            
    
