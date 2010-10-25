#-*- coding: utf-8 -*-
'''
Created on Sep 8, 2010

@author: ivan
'''
import gtk
from foobnix.regui.model.signal import FControl
from foobnix.util.const import EQUALIZER_LABLES
from foobnix.regui.model.eq_model import EqModel
from foobnix.util.fc import FC
from foobnix.util.mouse_utils import is_rigth_click
from foobnix.helpers.menu import Popup
from foobnix.helpers.my_widgets import ImageButton
import copy

def label(): 
    label = gtk.Label("–")
    label.show()
    return label

def empty(): 
    label = gtk.Label(" ")
    label.show()
    return label

def text(text): 
    label = gtk.Label(text)
    label.show()
    return label
 
class EqWindow(gtk.Window, FControl):
    
    def __init__(self, controls, collback):
        self.collback = collback 
        FControl.__init__(self, controls)        
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        
        self.set_title("Equalizer")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)
        self.connect("delete-event", self.hide_window)
        
        
        self.eq_lines = []
        for label in EQUALIZER_LABLES:
            self.eq_lines.append(EqLine(label, self.on_collback))
            
            
            
       
        lbox = gtk.VBox(False, 0)
        lbox.show()
        
        self.combo = gtk.combo_box_entry_new_text()
        self.combo.connect("changed", self.on_combo_chage)
        
        lbox.pack_start(self.top_row(), False, False, 0)
        lbox.pack_start(self.middle_lines_box(), False, False, 0)
        
        
        self.add(lbox)
        
        self.models = []
        self.default_models = []
        
    def on_restore_defaults(self,*a):
        self.models = []
        self.combo.get_model().clear()        
        self.append_all_models(copy.deepcopy(self.default_models))
        self.on_combo_chage()
        
    def on_button_press(self,w,e):
        print "click"
        if is_rigth_click(e):
            print "r click"
            menu = Popup()
            menu.add_item('Restore Defaults', gtk.STOCK_REFRESH,None)
            menu.show(e)
    
    def on_collback(self):
        pre = self.eq_lines[0].get_value()
        if float(pre)>=0:
            pre = "+"+pre
            
        self.db_text.set_text(pre+"db")
        self.collback()
    
    def on_enable_eq(self, w):
        FC().is_eq_enable = w.get_active()
    
    def on_save(self, *args):
        text = self.combo.get_active_text()
        find = False
        text_id = None 
        for model in self.models:
            if model.name == text:               
                model.set_values(self.get_active_values()[1:])
                find = True
                text_id = model.id
                break
        
        if not find:
            print self.get_active_values()[1:]
            self.models.append(EqModel(text, text, 0, self.get_active_values()[1:]))
            self.combo.append_text(text)
            text_id = text
        
        FC().eq_presets_default = text_id   
        
    def get_active_values(self):
        result = []
        for line in self.eq_lines:
            result.append(float(line.get_value()))
        
        return result

    def notify_chage_eq_line(self):
        self.get_active_values()    
        print self.get_active_values() 
    
    def append_all_models(self, models):
        self.models = models
        self.populate(models)
    
    def set_active(self, model_id):
        for i, c_model in enumerate(self.models):
            if c_model.id == model_id:
                self.combo.set_active(i)
                return
        
    def on_combo_chage(self, *a):        
        num = self.combo.get_active()
        if num >=0:        
            model = self.models[num]
            self.set_all_eq_span_values([model.preamp] + model.values)
            print num, model.name, self.get_active_values()
            self.collback()
        
    def populate(self, models):
        for model in models:
            self.combo.append_text(model.name)
    
    
    def set_active_preset(self, name):        
        self.presets_cache[name]
    
    def top_row(self):
        
        box = gtk.HBox(False, 0)
        box.show()
        
        self.on = gtk.ToggleButton("On")
        self.on.connect("toggled",self.on_enable_eq)
        #on.set_size_request(30,-1)        
        self.on.show()
        
        auto = gtk.ToggleButton("Auto")
        #auto.set_size_request(50,-1)
        auto.show()
        
        empt = empty()
        empt.set_size_request(65, -1)
        
        #auto.set_size_request(50,-1)
        auto.show()
        

        #combo = gtk.ComboBoxEntry()
        #self.combo.set_size_request(240, -1)
        self.combo.show()
        
        save = gtk.Button("Save")
        save.connect("clicked", self.on_save)
        
        save.show()
        
        
        resButton = ImageButton(gtk.STOCK_REFRESH)
        resButton.connect("clicked", self.on_restore_defaults)
        resButton.set_tooltip_text("Restore defaults presets")
        
        box.pack_start(self.on, False, False, 0)
        #box.pack_start(auto, False, True, 0)
        box.pack_start(empt, False, True, 0)        
        box.pack_start(self.combo, False, True, 0)        
        box.pack_start(save, False, True, 0)
        box.pack_start(gtk.Label(), True, True, 0)
        box.pack_start(resButton, False, True, 0)
        
        return box
    
    def dash_line(self):
        lables = gtk.VBox(False, 0)
        lables.show()
        lables.pack_start(label(), False, False, 0)
        lables.pack_start(label(), True, False, 0)
        lables.pack_start(label(), False, False, 0)
        lables.pack_start(empty(), False, False, 0)
        return lables
    
    def db_line(self):
        lables = gtk.VBox(False, 0)
        lables.show()
        lables.pack_start(text("+12db"), False, False, 0)
        
        self.db_text = text("0db")
        
        lables.pack_start(self.db_text, True, False, 0)
        lables.pack_start(text("-12db"), False, False, 0)
        lables.pack_start(empty(), False, False, 0)
        return lables
    
    def empty_line(self):
        lables = gtk.VBox(False, 0)
        lables.show()
        lables.pack_start(empty(), False, False, 0)
        lables.pack_start(empty(), True, False, 0)
        lables.pack_start(empty(), False, False, 0)
        lables.pack_start(empty(), False, False, 0)
        return lables
                
    def middle_lines_box(self):         
        lines_box = gtk.HBox(False, 0)
        lines_box.show()
        
        
            
        eq_iter = iter(self.eq_lines)
        
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        
        lines_box.pack_start(self.empty_line(), False, False, 0)
        lines_box.pack_start(self.db_line(), False, False, 0)
        lines_box.pack_start(self.empty_line(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(eq_iter.next(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.empty_line(), False, False, 0)
        
        return lines_box
    
    def set_all_eq_span_values(self, values):
        for i, eq_scale in enumerate(self.eq_lines):
            eq_scale.set_value(values[i])
        
    def on_load(self):
        self.on.set_active(FC().is_eq_enable)
   
    def destroy(self):
        self.hide()
        return True
    
    def show(self):
        self.show_all()

   
    def hide_window(self, *a):
        self.hide()
        return True
    
class EqLine(gtk.VBox):
        def __init__(self, text, callback, def_value=0):
            self.callback = callback
            self.text = text
            gtk.VBox.__init__(self, False, 0)
            self.show()
            
            adjustment = gtk.Adjustment(value=def_value, lower= -12, upper=12, step_incr=1, page_incr=2, page_size=0)
            self.scale = gtk.VScale(adjustment)
            self.scale.connect("change-value", self.on_change_value)
            self.scale.set_size_request(-1, 140)  
            self.scale.set_draw_value(False)      
            self.scale.set_inverted(True)       
            self.scale.show()
            
            """text under"""
            text = gtk.Label(text)
            text.show()
            
            self.pack_start(self.scale, False, False, 0)
            self.pack_start(text, False, False, 0)
        
        def on_change_value(self, *args):
            self.callback()
            
        
        def set_value(self, value):
            self.scale.set_value(value)
        
        def get_value(self):
            return "%.1f" % self.scale.get_value()   
