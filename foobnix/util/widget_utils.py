#-*- coding: utf-8 -*-
'''
Created on 29 нояб. 2010

@author: ivan
'''
from gi.repository import Gtk

class MenuStyleDecorator():
    def __init__(self):
        correct_style_element = Gtk.Window()
        correct_style_element.realize()
        self.style = correct_style_element.get_style()
        
    def apply(self, widget):
        style = self.style
        ## TODO: fix it
        return
        ##widget.modify_bg(Gtk.StateType.NORMAL, style.bg[Gtk.StateType.NORMAL])
        ##widget.modify_fg(Gtk.StateType.NORMAL, style.fg[Gtk.StateType.NORMAL])
        
        for childs in widget.get_children():
            for child in childs:
                widget.modify_bg(Gtk.StateType.NORMAL, style.bg[Gtk.StateType.NORMAL])
                child.modify_fg(Gtk.StateType.NORMAL, style.fg[Gtk.StateType.NORMAL])
        
