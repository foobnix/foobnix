#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.util import const, LOG
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click
from foobnix.helpers.menu import Popup
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.key_utils import KEY_RETURN, is_key, KEY_DELETE
from foobnix.util.fc import FC

class PlaylistTreeControl(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)

        """Column icon"""
        icon = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), stock_id=self.play_icon[0])
        icon.set_fixed_width(5)
        icon.set_min_width(5)
        """track number"""
        tracknumber = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.tracknumber[0])
        #tracknumber.set_sort_indicator(True)
        #tracknumber.set_sort_order(gtk.SORT_DESCENDING)
        #tracknumber.set_sort_column_id(2)


        """conlumt artist title"""
        description = gtk.TreeViewColumn('Artist - Title', gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        description.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        #description.set_resizable(True)
        description.set_expand(True)

        """time text"""
        time = gtk.TreeViewColumn('Time', gtk.CellRendererText(), text=self.time[0])
        time.set_fixed_width(5)
        time.set_min_width(5)

        self.append_column(icon)
        self.append_column(tracknumber)
        self.append_column(description)
        self.append_column(time)

        self.configure_send_drug()
        self.configure_recive_drug()
        
        self.set_playlist_plain()
        
    def set_playlist_tree(self):
        self.rebuild_as_tree()
        
    def set_playlist_plain(self):
        self.rebuild_as_plain()
        
    def on_key_release(self, w, e):
        if is_key(e, KEY_RETURN):
            self.active_current_song()
        elif is_key(e, KEY_DELETE):
            self.delete_selected()     
    
    def common_signle_random(self):
        LOG.debug("Repeat state", FC().repeat_state)
        if FC().repeat_state == const.REPEAT_SINGLE:
            return self.get_current_bean_by_UUID();
        
        if FC().is_order_random:               
            bean = self.get_random_bean()
            self.set_play_icon_to_bean(bean)
            return bean
    
    def next(self):
        bean  = self.common_signle_random()       
        if bean:
            return bean
    
        bean = self.get_next_bean_by_UUID(FC().repeat_state == const.REPEAT_ALL)
        
        if not bean:
            return
        
        self.set_play_icon_to_bean(bean)
        return bean

    def prev(self):
        bean  = self.common_signle_random()       
        if bean:
            return bean
    
        bean = self.get_prev_bean_by_UUID(FC().repeat_state == const.REPEAT_ALL)
        
        if not bean:
            return
        
        
        self.set_play_icon_to_bean(bean)
        return bean

    def append(self, bean):
        return super(PlaylistTreeControl, self).append(bean)

    
    def on_button_press(self, w, e):
        self.controls.notetabs.set_active_tree(self)
        if is_double_left_click(e):
            self.controls.play_selected_song()
        if is_rigth_click(e):
            menu = Popup()
            menu.add_item('Play', gtk.STOCK_MEDIA_PLAY, self.controls.play_selected_song, None)
            menu.add_item('Download', gtk.STOCK_ADD, self.controls.dm.append_tasks, self.get_all_selected_beans())
            menu.add_item('Save as', gtk.STOCK_SAVE_AS, self.controls.save_beans_to, self.get_all_selected_beans())
            menu.add_separator()
            text = self.get_selected_bean().text
            menu.add_item('Copy to Search Line', gtk.STOCK_COPY, self.controls.searchPanel.set_search_text, text)
            menu.show(e)
