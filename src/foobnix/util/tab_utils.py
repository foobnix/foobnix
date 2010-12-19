'''
Created on Dec 16, 2010

@author: zavlab1
'''
import gtk
from foobnix.util.key_utils import is_key
from foobnix.util.fc import FC

def get_text_label_from_tab(notebook, tab_child, need_box_lenth = False):
        eventbox = notebook.get_tab_label(tab_child)
        box = eventbox.get_child()
        box_lenth = len(box.get_children())
        if type(box.get_children()[0]) == gtk.Label:
            label_object = box.get_children()[0]
        else: label_object = box.get_children()[1]
        text_of_label = label_object.get_label()
        if need_box_lenth:
            return text_of_label, box_lenth
        else: return text_of_label
        
def on_rename_tab(notebook, tab_child, angle = 0):
        
        """get old label value"""
        n = notebook.page_num(tab_child)
        old_label_text, box_lenth = get_text_label_from_tab(notebook, tab_child, True)
        
        window = gtk.Window()
        window.set_decorated(False)
        window.set_position(gtk.WIN_POS_MOUSE)
        window.set_border_width(5)
        entry = gtk.Entry()
        entry.set_text(old_label_text)
        entry.show()
        
        def on_key_press(w, e):
            if is_key(e, 'Escape'):
                window.hide()
                entry.set_text(old_label_text)
            elif is_key(e, 'Return'):
                window.hide()
                new_label_text = entry.get_text()
                if new_label_text:
                    label = gtk.Label(new_label_text + ' ')
                    label.set_angle(angle)
                    if angle:
                        new_vbox = gtk.VBox()
                        if box_lenth > 1:
                            new_vbox.pack_start(notebook.button(tab_child.get_child()), False, False)
                        new_vbox.pack_end(label, False, False)
                    else:
                        new_vbox = gtk.HBox()
                        if box_lenth > 1:
                            new_vbox.pack_end(notebook.button(tab_child.get_child()), False, False)
                        new_vbox.pack_start(label, False, False)
                    event = gtk.EventBox()
                    event.add(new_vbox)
                    event = notebook.tab_menu_creator(event, tab_child)
                    event.set_visible_window(False)
                    event.connect("button-press-event", notebook.on_button_press)
                    event.show_all()
                    notebook.set_tab_label(tab_child, event)
                    FC().tab_names[n] = new_label_text
        
        def on_focus_out(*a):
            window.hide()
            entry.set_text(old_label_text)
            
        window.connect("key_press_event", on_key_press)
        window.connect("focus-out-event", on_focus_out)
        window.add(entry)
        window.show_all()