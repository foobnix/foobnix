#-*- coding: utf-8 -*-
'''
Created on Sep 8, 2010

@author: ivan
'''
import gtk
from foobnix.regui.model.signal import FControl
import gst

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
 
class EQContols(gtk.Window, FControl):
    
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
                
    
    class EqLine(gtk.VBox):
        def __init__(self, text, manager, def_value=0):
            self.manager = manager
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
            self.manager.change_value(self.text, self.get_value())
            print self.text, self.get_value()
        
        def set_value(self, value):
            self.scale.set_value(value)
        
        def get_value(self):
            return self.scale.get_value()
    
    class EqManager():
        def __init__(self, engine):
            self.engine = engine
            self.values = []   
            
        def set_values(self, values): 
            self.values = values           
            self.engine.set_values(self.values)
        
        def change_value(self, id, value):    
            labels = ["PREAMP", "29", "59", "119", "237", "474", "1K", "2K", "4K", "8K", "15K"]
            index = labels.index(id)
            print index, self.values
            self.values[index] = value
            #self.values[index] = []
            self.engine.set_values(self.values)
            
        
    
    def middle_lines_box(self):         
        lines_box = gtk.HBox(False, 0)
        lines_box.show()
        
        self.labels = ["PREAMP", "29", "59", "119", "237", "474", "1K", "2K", "4K", "8K", "15K"]
        self.scales = []
        for label in self.labels:
            self.scales.append(self.EqLine(label, self.manager))
        
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.scales[0], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        
        lines_box.pack_start(self.empty_line(), False, False, 0)
        lines_box.pack_start(self.db_line(), False, False, 0)
        lines_box.pack_start(self.empty_line(), False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        
        lines_box.pack_start(self.scales[1], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.scales[2], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.scales[3], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.scales[4], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.scales[5], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.scales[6], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.scales[7], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.scales[8], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.scales[9], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.scales[10], False, False, 0)
        lines_box.pack_start(self.dash_line(), False, False, 0)
        lines_box.pack_start(self.empty_line(), False, False, 0)
        
        return lines_box
    
    def pupulate_values(self, values):
        self.manager.set_values(values)
        for i, scale in enumerate(self.scales):
            scale.set_value(values[i])
        
        
         
    def __init__(self, controls, engine):
        self.engine = engine
        FControl.__init__(self, controls)        
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_title("Equalizer")
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)
        #self.connect("delete-event", self.hide_window)
       
        lbox = gtk.VBox(False, 0)
        lbox.show()
        
        self.manager = self.EqManager(engine)
                
        
        lbox.pack_start(self.top_row(), False, False, 0)
        lbox.pack_start(self.middle_lines_box(), False, False, 0)
        
        self.add(lbox)

    def on_load(self):
        pass
   
    def destroy(self):
        self.hide()
        return True
    
    def show(self):
        self.show_all()

   
    def hide_window(self, *a):
        self.hide()
        return True

class EQEngine():
    def __init__(self):
        self.player = gst.Pipeline("player")
        source = gst.element_factory_make("filesrc", "file-source")
        decoder = gst.element_factory_make("mad", "mp3-decoder")
        conv = gst.element_factory_make("audioconvert", "converter")
        sink = gst.element_factory_make("alsasink", "alsa-output")
        self.equalizer = gst.element_factory_make("equalizer-10bands")
        
        self.player.add(source, decoder, conv, self.equalizer, sink)
        gst.element_link_many(source, decoder, conv, self.equalizer, sink)

        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
        
    def set_values(self, values):
        for i, value in enumerate(values[1:]):            
            self.equalizer.set_property("band%s" % i, value)
        print "Engine", values

    def play(self, path):
        self.player.get_by_name("file-source").set_property("location", path)
        self.player.set_state(gst.STATE_PLAYING)

    
    def settings(self):            
            self.presets.append(["Custom", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            self.presets.append(["Default", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
            self.presets.append(["Classical", 0, 0, 0, 0, 0, 0, 0, -7.2, -7.2, -7.2, -9.6])
            self.presets.append(["Club", 0, 0, 0, 8, 5.6, 5.6, 5.6, 3.2, 0, 0, 0])
            self.presets.append(["Dance",
                    0, 9.6, 7.2, 2.4, 0, 0, -5.6, -7.2, -7.2, 0, 0])
            self.presets.append(["Full Bass",
                    0, -8, 9.6, 9.6, 5.6, 1.6, -4, -8, -10.4, -11.2, -11.2])
            self.presets.append(["Full Bass and Treble",
                    0, 7.2, 5.6, 0, -7.2, -4.8, 1.6, 8, 11.2, 12, 12])
            self.presets.append(["Full Treble",
                    0, -9.6, -9.6, -9.6, -4, 2.4, 11.2, 16, 16, 16, 16.8])
            self.presets.append(["Laptop Speakers and Headphones",
                    0, 4.8, 11.2, 5.6, -3.2, -2.4, 1.6, 4.8, 9.6, 11.9, 11.9])
            self.presets.append(["Large Hall",
                    0, 10.4, 10.4, 5.6, 5.6, 0, -4.8, -4.8, -4.8, 0, 0])
            self.presets.append(["Live",
                    0, -4.8, 0, 4, 5.6, 5.6, 5.6, 4, 2.4, 2.4, 2.4])
            self.presets.append(["Party",
                    0, 7.2, 7.2, 0, 0, 0, 0, 0, 0, 7.2, 7.2])
            self.presets.append(["Pop",
                    0, -1.6, 4.8, 7.2, 8, 5.6, 0, -2.4, -2.4, -1.6, -1.6])
            self.presets.append(["Reggae",
                    0, 0, 0, 0, -5.6, 0, 6.4, 6.4, 0, 0, 0])
            self.presets.append(["Rock",
                    0, 8, 4.8, -5.6, -8, -3.2, 4, 8.8, 11.2, 11.2, 11.2])
            self.presets.append(["Ska",
                    0, -2.4, -4.8, -4, 0, 4, 5.6, 8.8, 9.6, 11.2, 9.6])
            self.presets.append(["Soft",
                    0, 4.8, 1.6, 0, -2.4, 0, 4, 8, 9.6, 11.2, 12])
            self.presets.append(["Soft Rock",
                    0, 4, 4, 2.4, 0, -4, -5.6, -3.2, 0, 2.4, 8.8])
            self.presets.append(["Techno",
                    0, 8, 5.6, 0, -5.6, -4.8, 0, 8, 9.6, 9.6, 8.8])



          
    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.button.set_label("Start")
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            self.button.set_label("Start")
            err, debug = message.parse_error()
            print "Error: %s" % err, debug

    

if __name__ == '__main__':
    engine = EQEngine()
    engine.play("/home/ivan/Музыка/1/12.mp3")
    
    settting_line = [-12, -10, -7, -5, -1, 0, 1, 3, 5, 7, 12]
    engine.set_values(settting_line)
    
    eq = EQContols(None, engine)
    eq.pupulate_values(settting_line)
    eq.on_load()
    eq.connect("destroy", lambda * a:gtk.main_quit())
    eq.show()
    gtk.main()




