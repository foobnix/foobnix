#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.treeview import TreeViewControl
import gtk
class PlaylistControl(TreeViewControl):
    def __init__(self):
        TreeViewControl.__init__(self)
        self.set_reorderable(True)

        """Column icon"""                
        icon = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), stock_id=self.play_icon)
        
        """conlumt artist title"""
        description = gtk.TreeViewColumn('Artist - Title', gtk.CellRendererText(), text=self.text)
        description.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        description.set_resizable(True)
        description.set_expand(True)
        
        """time text"""
        time = gtk.TreeViewColumn('Time', gtk.CellRendererText(), text=self.time)
        time.set_fixed_width(5)
        time.set_min_width(5)
        
        self.append_column(icon)
        self.append_column(description)
        self.append_column(time)
   
    def append(self, bean):        
        super(PlaylistControl, self).append(None, text=bean.text, play_icon=bean.play_icon, time=bean.time)

   
