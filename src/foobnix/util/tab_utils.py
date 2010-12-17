'''
Created on Dec 16, 2010

@author: zavlab1
'''
import gtk

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