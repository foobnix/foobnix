#-*- coding: utf-8 -*-
'''
Created on Sep 8, 2010

@author: ivan
'''
import gtk

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
 
class EQ():
    
    def top_row(self):
        
        box = gtk.HBox(False, 0)
        box.show()
        
        on = gtk.ToggleButton("On")
        #on.set_size_request(30,-1)        
        on.show()
        
        auto = gtk.ToggleButton("Auto")
        #auto.set_size_request(50,-1)
        auto.show()
        
        empt = empty()
        empt.set_size_request(65, -1)
        
        #auto.set_size_request(50,-1)
        auto.show()
        
        combo = gtk.combo_box_entry_new_text()
        combo.append_text("Will be soon....")
        combo.set_active(0)

        #combo = gtk.ComboBoxEntry()
        combo.set_size_request(240, -1)
        combo.show()
        
        save = gtk.Button("Save")        
        save.show()
        
        box.pack_start(on, False, False, 0)
        box.pack_start(auto, False, True, 0)
        box.pack_start(empt, False, True, 0)        
        box.pack_start(combo, False, True, 0)        
        box.pack_start(save, False, True, 0)
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
        lables.pack_start(text("+0db"), True, False, 0)
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
                
    
    def equlalizer_line(self, text):
        
        vbox = gtk.VBox(False, 0)
        vbox.show()
        
        adjustment = gtk.Adjustment(value=0, lower=-12, upper=12, step_incr=1, page_incr=2, page_size=0)
        scale = gtk.VScale(adjustment)
        scale.set_size_request(-1, 140)  
        scale.set_draw_value(False)      
        scale.set_inverted(True)       
        scale.show()
        
        """text under"""
        text = gtk.Label(text)
        text.show()
        
        vbox.pack_start(scale, False, False, 0)
        vbox.pack_start(text, False, False, 0)
                
                
        return vbox
    
    def middle_lines(self):         
        lines = gtk.HBox(False, 0)
        lines.show()
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.equlalizer_line("PREAMP"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        
        lines.pack_start(self.empty_line(), False, False, 0)
        lines.pack_start(self.db_line(), False, False, 0)
        lines.pack_start(self.empty_line(), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        
        lines.pack_start(self.equlalizer_line("29"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.equlalizer_line("59"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.equlalizer_line("119"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.equlalizer_line("237"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.equlalizer_line("474"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.equlalizer_line("1K"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.equlalizer_line("2K"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.equlalizer_line("4K"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.equlalizer_line("8K"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.equlalizer_line("15K"), False, False, 0)
        lines.pack_start(self.dash_line(), False, False, 0)
        lines.pack_start(self.empty_line(), False, False, 0)
        
        return lines
     
    def show(self):
        self.window.show()     
    
    def hide(self):
        self.window.hide()         
    
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("Equalizer")
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.set_resizable(False)
        self.window.connect("destroy", lambda *a:gtk.main_quit())
       
        lbox = gtk.VBox(False, 0)
        lbox.show()
                
        
        lbox.pack_start(self.top_row(), False, False, 0)
        lbox.pack_start(self.middle_lines(), False, False, 0)
        
        self.window.add(lbox)
        self.window.show()
        
        #self.window.set_size_request(400,250)
        
        gtk.main()


eq = EQ()
eq.show()
gtk.main()
