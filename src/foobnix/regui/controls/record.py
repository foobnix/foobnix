'''
Created on Mar 23, 2011

@author: zavlab1
'''
import os
import gtk
import gst
import shutil
import logging

from subprocess import Popen, PIPE
from foobnix.helpers.dialog_entry import FileSavingDialog



class RadioRecord(gtk.ToggleButton):
    def __init__(self, controls):
        gtk.ToggleButton.__init__(self)
        self.controls = controls
        
        rec_image = gtk.image_new_from_stock(gtk.STOCK_MEDIA_RECORD, gtk.ICON_SIZE_BUTTON)
        rec_image.show()
        self.add(rec_image)
        self.set_relief(gtk.RELIEF_NONE)
        self.set_focus_on_click(False)
        self.connect("toggled", self.on_toggle)
        self.set_tooltip_text(_("Record radio"))
        self.set_no_show_all(True)
        self.hide()
        
    def on_toggle(self, a=None):
        engine = self.controls.media_engine
              
        if hasattr(engine, 'pipeline'):
            if gst.STATE_PLAYING in engine.pipeline.get_state():
                engine.pipeline.set_state(gst.STATE_NULL)
                if os.path.isfile(engine.radio_path):
                    name = os.path.basename(engine.radio_path)
                else:
                    name = "radio_record"
                current_name = name
                
                temp_file = os.path.join("/tmp", name)
                if not os.path.exists(temp_file):
                    logging.warning(_("So file doesn't exist. Pehaps it wasn't create yet."))
                    return
                if not os.path.splitext(current_name)[1]:
                    mime = Popen("file -i " + temp_file, shell=True, stdout=PIPE).communicate()[0]
                    
                    if 'mpeg' in mime:
                        current_name = name + '.mp3'
                    elif 'ogg' in mime:
                        current_name = name + '.ogg'
                    
                def func(filename, folder):
                    shutil.move(temp_file, os.path.join(folder, filename))
                    
                FileSavingDialog(_("Save file as ..."), func, args = None, current_folder=os.path.expanduser("~"), current_name=current_name)
                return
        bean = self.controls.notetabs.get_current_tree().get_current_bean_by_UUID()
        engine.record_radio(bean)