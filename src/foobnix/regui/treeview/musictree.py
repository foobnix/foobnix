#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.treeview import TreeViewControl
import gtk
class MusicTreeControl(TreeViewControl):
    def __init__(self):
        TreeViewControl.__init__(self)
        self.set_reorderable(False)
        
        """column config"""
        column = gtk.TreeViewColumn("Title", gtk.CellRendererText(), text=self.POS_TEXT, font=self.POS_FONT)
        column.set_resizable(True)
        self.append_column(column)
        
