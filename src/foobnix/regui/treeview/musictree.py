#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.treeview import TreeViewControl
import gtk
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click
from foobnix.regui.state import LoadSave
from foobnix.helpers.menu import Popup
from foobnix.util.fc import FC
from foobnix.util import LOG
class MusicTreeControl(TreeViewControl, LoadSave):
    def __init__(self, controls):
        TreeViewControl.__init__(self, controls)
        
        """column config"""
        column = gtk.TreeViewColumn("Music Lybrary", gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        column.set_resizable(True)
        self.append_column(column)
        
        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example1", 0, 0)], gtk.gdk.ACTION_COPY)
        #self.enable_model_drag_dest([("example1", 0, 0)], gtk.gdk.ACTION_COPY)
    
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            bean = self.get_selected_bean()
            self.controls.append_to_new_notebook(bean.text, [bean])
            print "double left"
        if is_rigth_click(e):            
                menu = Popup()
                menu.add_item(_("Update Music Tree"), gtk.STOCK_REFRESH, self.controls.update_music_tree, None)
                #menu.add_item(_("Play"), gtk.STOCK_MEDIA_PLAY, self.populate_playlist, None)
                menu.add_item(_("Add folder"), gtk.STOCK_OPEN, self.add_folder, None)
                menu.show(e)
    
    def add_folder(self):
        chooser = gtk.FileChooserDialog(title=_("Choose directory with music"),
                                        action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        chooser.set_select_multiple(True)
        if FC().last_music_path:
                chooser.set_current_folder(FC().last_music_path)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            paths = chooser.get_filenames()
            path = paths[0]
            FC().last_music_path = path[:path.rfind("/")]
            for path in paths:
                if path in FC().music_paths:
                    pass
                else:                                       
                    FC().music_paths.append(path)
                    self.controls.preferences.on_load()                     
                    LOG.info("News music paths", FC().music_paths)

            self.controls.update_music_tree()

        elif response == gtk.RESPONSE_CANCEL:
            LOG.info('Closed, no files selected')
        chooser.destroy()        
      
    def on_load(self):
        self.controls.load_music_tree()
        pass
    
    def on_save(self):
        pass
