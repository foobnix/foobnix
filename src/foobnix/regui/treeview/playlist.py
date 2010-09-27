#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.treeview import TreeViewControl
import gtk
from foobnix.util.mouse_utils import is_double_left_click
class PlaylistControl(TreeViewControl):
    def __init__(self):
        TreeViewControl.__init__(self)
        self.set_reorderable(True)

        """Column icon"""                
        icon = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), stock_id=self.play_icon[0])
        icon.set_fixed_width(5)
        icon.set_min_width(5)
        """track number"""
        tracknumber = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.tracknumber[0])
        
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
   
    def next(self):
        current = self.get_selected_bean()
        current.index =+1
        self.repopulate(current.index)
    
    def prev(self):
        current = self.get_selected_bean()
        current.index =-1
        self.repopulate(current.index)
     
    def repopulate(self, index):
        all = self.get_all_beans()
        self.clear()
        for bean in all:
            if bean.index == index:                    
                bean.play_icon = gtk.STOCK_MEDIA_PLAY
            else:
                bean.play_icon = None
            self.append(bean)
         
    def on_button_press(self,w,e):
        if is_double_left_click(e):
            current = self.get_selected_bean()
            self.repopulate(current.index)
            
        