#-*- coding: utf-8 -*-
'''
Created on 29 нояб. 2010

@author: ivan
'''
import gtk

class MenuStyleDecorator():
    def __init__(self):
        correct_style_element = gtk.Window()
        correct_style_element.realize()
        self.style = correct_style_element.get_style()
        
    def apply(self, widget):
        style = self.style
        widget.modify_bg(gtk.STATE_NORMAL, style.bg[gtk.STATE_NORMAL])
        widget.modify_fg(gtk.STATE_NORMAL, style.fg[gtk.STATE_NORMAL])
        
        for childs in widget.get_children():
            for child in childs:
                widget.modify_bg(gtk.STATE_NORMAL, style.bg[gtk.STATE_NORMAL])
                child.modify_fg(gtk.STATE_NORMAL, style.fg[gtk.STATE_NORMAL])
        
