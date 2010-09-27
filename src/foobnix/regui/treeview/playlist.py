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
        icon = gtk.TreeViewColumn('', gtk.CellRendererPixbuf(), stock_id=self.play_icon[0])
        
        """track number"""
        tracknumber = gtk.TreeViewColumn('', gtk.CellRendererText(), text=self.tracknumber[0])
        
        """conlumt artist title"""
        description = gtk.TreeViewColumn('Artist - Title', gtk.CellRendererText(), text=self.text[0])
        description.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        description.set_resizable(True)
        description.set_expand(True)
        
        """time text"""
        time = gtk.TreeViewColumn('Time', gtk.CellRendererText(), text=self.time[0])
        time.set_fixed_width(5)
        time.set_min_width(5)
        
        self.append_column(icon)
        self.append_column(tracknumber)
        self.append_column(description)
        self.append_column(time)
