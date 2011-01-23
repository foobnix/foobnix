'''
Created on Sep 27, 2010

@author: ivan
'''
import gtk

from foobnix.util import const
from foobnix.util.fc import FC
from foobnix.regui.state import LoadSave
from foobnix.helpers.toolbar import MyToolbar
from foobnix.regui.model.signal import FControl
from foobnix.helpers.my_widgets import ImageButton, EventLabel


class PlaybackControlsNotUsedOld(FControl, MyToolbar, LoadSave):
    def __init__(self, controls): 
        FControl.__init__(self, controls)    
        MyToolbar.__init__(self)   
        self.add_separator()
        self.add_button("Stop", gtk.STOCK_MEDIA_STOP, controls.state_stop, None)   
        self.add_button("Play", gtk.STOCK_MEDIA_PLAY, controls.state_play, None)
        self.add_button("Pause", gtk.STOCK_MEDIA_PAUSE, controls.state_pause, None)
        self.add_button("Previous", gtk.STOCK_MEDIA_PREVIOUS, controls.prev, None)
        self.add_button("Next", gtk.STOCK_MEDIA_NEXT, controls.next, None)
        self.add_separator()
        
    def on_load(self): pass
    def on_save(self): pass

class OrderShuffleControls(FControl, gtk.HBox, LoadSave):
    def __init__(self, controls): 
        gtk.HBox.__init__(self, False)
        
        self.rlabel = EventLabel(text="S", func=lambda * a: self.on_random())
        self.olabel = EventLabel(text="R", func=lambda * a: self.on_order())
        
        self.pack_start(self.rlabel)
        self.pack_start(gtk.Label(" "))
        self.pack_start(self.olabel)
        
        self.pack_start(gtk.SeparatorToolItem())
    
    def update(self):
        if FC().is_order_random:
            self.rlabel.set_markup("<b>S</b>")
            self.rlabel.set_tooltip_text(_("Shuffle on"))
            
        else:
            self.rlabel.set_markup("S")
            self.rlabel.set_tooltip_text(_("Shuffle off"))
            
        if FC().repeat_state == const.REPEAT_ALL:
            self.olabel.set_markup("<b>R</b>")
            self.olabel.set_tooltip_text(_("Repeat all"))            
        elif FC().repeat_state == const.REPEAT_SINGLE:
            self.olabel.set_markup("<b>R1</b>")
            self.olabel.set_tooltip_text(_("Repeat single"))
        else:
            self.olabel.set_markup("R")
            self.olabel.set_tooltip_text(_("Repeat off"))
        
    def on_random(self, *a):
        FC().is_order_random = not FC().is_order_random
        self.update()
    
    def on_order(self):
        if FC().repeat_state == const.REPEAT_ALL:
            FC().repeat_state = const.REPEAT_SINGLE
        elif FC().repeat_state == const.REPEAT_SINGLE:
            FC().repeat_state = const.REPEAT_NO
        elif FC().repeat_state == const.REPEAT_NO:
            FC().repeat_state = const.REPEAT_ALL
        self.update()
            
    def on_load(self): 
        self.update()
        
    def on_save(self): pass        
    
class OrderShuffleControls_ZAVLAB(FControl, gtk.HBox, gtk.Tooltips, LoadSave):
    def __init__(self, controls): 
        gtk.HBox.__init__(self, False)
                
        self.order = gtk.ToggleButton()
        order_image = gtk.image_new_from_stock(gtk.STOCK_REDO, gtk.ICON_SIZE_BUTTON)
        self.order.add(order_image)
        self.order.set_relief(gtk.RELIEF_NONE)
        self.order.set_focus_on_click(False)
        self.order.set_has_tooltip(True)
        self.order.connect("button-press-event", self.on_order)
        
        self.pack_start(self.order)
        
        self.repeat = gtk.ToggleButton()
        repeat_image = gtk.image_new_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_BUTTON)
        self.repeat.add(repeat_image)
        self.repeat.set_relief(gtk.RELIEF_NONE)
        self.repeat.set_focus_on_click(False)    
        self.repeat.set_has_tooltip(True)
        
        self.repeat.connect("button-press-event", self.choise)
        self.pack_start(self.repeat)
                
        self.pack_start(gtk.SeparatorToolItem())
        
        self.menu = gtk.Menu()
        self.item_all = gtk.CheckMenuItem(_("Repeat all"))
        self.item_all.connect("button-press-event", self.on_repeat)
        self.menu.append(self.item_all)
        self.item_single = gtk.CheckMenuItem(_("Repeat single"))
        self.item_single.connect("button-press-event", lambda item, *a: self.on_repeat(item, False))
        self.menu.append(self.item_single)
       
    def choise(self, widget, event):
            self.menu.popup(None, None, None, event.button, event.time)
            self.menu.show_all()
            
    def on_load(self):
        if FC().is_order_random:
            self.order.set_active(True)
            self.order.set_tooltip_text(_("Shuffle on"))
        else:
            self.order.set_active(False)
            self.order.set_tooltip_text(_("Shuffle off"))
            
        if FC().repeat_state == const.REPEAT_ALL:
            self.repeat.set_active(True)
            self.repeat.set_tooltip_text(_("Repeat all"))
            self.item_all.set_active(True)            
        elif FC().repeat_state == const.REPEAT_SINGLE:
            self.repeat.set_active(True)
            self.repeat.set_tooltip_text(_("Repeat single"))
            self.item_single.set_active(True)
        else:
            self.repeat.set_active(False)
            self.repeat.set_tooltip_text(_("Repeat off"))
        
    def on_order(self, *a):
        FC().is_order_random = not FC().is_order_random
        if FC().is_order_random:
            self.order.set_tooltip_text(_("Shuffle on"))
        else:
            self.order.set_tooltip_text(_("Shuffle off"))
            
    def on_repeat(self, item, all=True):
        is_active = item.get_active()
        for menu_item in self.menu: 
            menu_item.set_active(False)
        if all:
            if not is_active:
                FC().repeat_state = const.REPEAT_ALL
                self.repeat.set_tooltip_text(_("Repeat all"))
                self.repeat.set_active(True)
            else:
                FC().repeat_state = const.REPEAT_NO
                item.set_active(True) #because signal "toggled" will change the value to the opposite
                self.repeat.set_active(False)
        elif not all:
            if not is_active:
                FC().repeat_state = const.REPEAT_SINGLE
                self.repeat.set_tooltip_text(_("Repeat single"))
                self.repeat.set_active(True)
            else:
                FC().repeat_state = const.REPEAT_NO
                item.set_active(True) #because signal "toggled" will change the value to the opposite  
                self.repeat.set_active(False)
                             
    
    def on_save(self): pass    
    
class PlaybackControls(FControl, gtk.HBox, LoadSave):
    def __init__(self, controls): 
        gtk.HBox.__init__(self, False)
        self.pack_start(gtk.SeparatorToolItem())
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_STOP, controls.state_stop, _("Stop")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_PLAY, controls.state_play, _("Play")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_PAUSE, controls.state_play_pause, _("Pause")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_PREVIOUS, controls.prev, _("Previous")))
        self.pack_start(ImageButton(gtk.STOCK_MEDIA_NEXT, controls.next, _("Next")))
        self.pack_start(gtk.SeparatorToolItem())
        
        
    def on_load(self): pass
    def on_save(self): pass    
