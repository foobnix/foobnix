'''
Created on Mar 23, 2011

@author: zavlab1
'''

import gtk
import gst

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
        
    def on_toggle(self, *a):
        engine = self.controls.media_engine
        engine.pipeline.get_state() 
        if hasattr(engine, 'pipeline'):
            if engine.pipeline.get_state()[1] == gst.STATE_PLAYING:
                engine.state_stop()
                return
        bean = self.controls.notetabs.get_current_tree().get_current_bean_by_UUID()
        engine.record_radio(bean)