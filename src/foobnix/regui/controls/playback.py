'''
Created on Sep 27, 2010

@author: ivan
'''

from gi.repository import Gtk

from foobnix.util import const
from foobnix.fc.fc import FC
from foobnix.regui.state import LoadSave
from foobnix.helpers.toolbar import MyToolbar
from foobnix.regui.model.signal import FControl
from foobnix.helpers.my_widgets import ImageButton, EventLabel


class PlaybackControlsNotUsedOld(FControl, MyToolbar, LoadSave):
    def __init__(self, controls): 
        FControl.__init__(self, controls)    
        MyToolbar.__init__(self)   
        self.add_separator()
        self.add_button("Stop", Gtk.STOCK_MEDIA_STOP, controls.state_stop, None)
        self.add_button("Play", Gtk.STOCK_MEDIA_PLAY, controls.state_play, None)
        self.add_button("Pause", Gtk.STOCK_MEDIA_PAUSE, controls.state_pause, None)
        self.add_button("Previous", Gtk.STOCK_MEDIA_PREVIOUS, controls.prev, None)
        self.add_button("Next", Gtk.STOCK_MEDIA_NEXT, controls.next, None)
        self.add_separator()
        
    def on_load(self): pass
    def on_save(self): pass

class OrderShuffleControls(FControl, Gtk.HBox, LoadSave):
    def __init__(self, controls):
        Gtk.HBox.__init__(self, False)
        
        self.toggle_buttons = OrderShuffleControls_ZAVLAB(controls)
        
        self.rlabel = EventLabel(text="S", func=lambda * a: self.on_random())
        self.olabel = EventLabel(text="R", func=lambda * a: self.on_order())
        
        self.pack_start(self.rlabel, False, False, 0)
        self.pack_start(Gtk.Label(" "), False, False, 0)
        self.pack_start(self.olabel, False, False, 0)
        self.pack_start(self.toggle_buttons, False, False, 0)
        
        self.pack_start(Gtk.SeparatorToolItem(), False, False, 0)
    
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
        if FC().order_repeat_style == "ToggleButtons":
            self.toggle_buttons.on_load()
            self.olabel.hide()
            self.rlabel.hide()
            self.toggle_buttons.show()
        else:
            self.update()
            self.toggle_buttons.hide()
            self.olabel.show()
            self.rlabel.show()
            
        
    def on_save(self): pass        
    
class OrderShuffleControls_ZAVLAB(FControl, Gtk.HBox, LoadSave):
    def __init__(self, controls): 
        Gtk.HBox.__init__(self, False)
                
        self.order = Gtk.ToggleButton()
        order_image = Gtk.Image.new_from_stock(Gtk.STOCK_REDO, Gtk.IconSize.BUTTON)
        self.order.add(order_image)
        self.order.set_relief(Gtk.ReliefStyle.NONE)
        self.order.set_focus_on_click(False)

        self.order.connect("button-press-event", self.on_order)
        
        self.pack_start(self.order, False, False, 0)
        
        self.repeat = Gtk.ToggleButton()
        repeat_image = Gtk.Image.new_from_stock(Gtk.STOCK_REFRESH, Gtk.IconSize.BUTTON)
        self.repeat.add(repeat_image)
        self.repeat.set_relief(Gtk.ReliefStyle.NONE)
        self.repeat.set_focus_on_click(False)    
        
        try:
            self.order.set_has_tooltip(True)
            self.repeat.set_has_tooltip(True)
        except:
            pass
        
        self.repeat.connect("button-press-event", self.choise)
        self.pack_start(self.repeat, False, False, 0)
                
        #self.pack_start(Gtk.SeparatorToolItem())
        
        self.menu = Gtk.Menu()
        self.item_all = Gtk.CheckMenuItem(_("Repeat all"))
        self.item_all.connect("button-press-event", self.on_repeat)
        self.menu.append(self.item_all)
        self.item_single = Gtk.CheckMenuItem(_("Repeat single"))
        self.item_single.connect("button-press-event", lambda item, *a: self.on_repeat(item, False))
        self.menu.append(self.item_single)
        
    def choise(self, widget, event):
            self.menu.popup(None, None, None, None, event.button, event.time)
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
    
class PlaybackControls(FControl, Gtk.HBox, LoadSave):
    def __init__(self, controls): 
        Gtk.HBox.__init__(self, False)
        self.pack_start(Gtk.SeparatorToolItem(), False, False, 0)
        self.pack_start(ImageButton(Gtk.STOCK_MEDIA_STOP, controls.state_stop, _("Stop")), False, False, 0)
        self.pack_start(ImageButton(Gtk.STOCK_MEDIA_PLAY, controls.state_play, _("Play")), False, False, 0)
        self.pack_start(ImageButton(Gtk.STOCK_MEDIA_PAUSE, controls.state_play_pause, _("Pause")), False, False, 0)
        self.pack_start(ImageButton(Gtk.STOCK_MEDIA_PREVIOUS, controls.prev, _("Previous")), False, False, 0)
        self.pack_start(ImageButton(Gtk.STOCK_MEDIA_NEXT, controls.next, _("Next")), False, False, 0)
        self.pack_start(Gtk.SeparatorToolItem(), False, False, 0)
        
        
    def on_load(self): pass
    def on_save(self): pass    
