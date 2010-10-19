#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.treeview import TreeViewControl
import gtk
from random import randint
from foobnix.util import const
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click
from foobnix.cue.cue_reader import CueReader
from foobnix.regui.model import FModel
from foobnix.helpers.menu import Popup

class PlaylistControl(TreeViewControl):
    def __init__(self, controls):
        TreeViewControl.__init__(self, controls)

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

        self.index = -1
        
        self.configure_send_drug()
        self.configure_recive_drug()
        
        self.set_playlist_plain()
        
    def set_playlist_tree(self):
        self.rebuild_as_tree()
        
    def set_playlist_plain(self):
        self.rebuild_as_plain()
        
    def on_key_release(self, w, e):
        if gtk.gdk.keyval_name(e.keyval) == 'Return':
            self.active_current_song()

    def next(self, rnd=False, lopping=const.LOPPING_LOOP_ALL):
        if lopping == const.LOPPING_LOOP_ALL:
            if not rnd:
                self.index += 1
                if self.index == self.count_index:
                    self.index = 0
            else:
                self.index = randint(0, self.count_index)
        elif lopping == const.LOPPING_DONT_LOOP:
            return None
        #self.repopulate(self.index)
        self.set_play_icon_to_selected_bean()
        return self.get_bean_by_position(self.index)

    def prev(self, rnd=False, lopping=const.LOPPING_LOOP_ALL):
        if lopping == const.LOPPING_LOOP_ALL:
            if not rnd:
                self.index -= 1
                if self.index < 0:
                    self.index = self.count_index - 1
            else:
                self.index = randint(0, self.count_index)
        elif lopping == const.LOPPING_DONT_LOOP:
            return None
        self.set_play_icon_to_selected_bean()
        return self.get_bean_by_position(self.index)

    def append(self, bean):
        value = None
        if bean.path and bean.path.endswith(".cue"):
            reader = CueReader(bean.path)
            beans = reader.get_common_beans()
            for bean in beans:
                value = super(PlaylistControl, self).append(bean)
        else:
            value = super(PlaylistControl, self).append(bean)
        return value


    def active_current_song(self):
        current = self.get_selected_bean()
        print current
        self.index = current.index
        if current.is_file:
            self.set_play_icon_to_selected_bean()


        """play song"""
        self.controls.play(current)

        """update song info"""
        self.controls.update_info_panel(current)

        """set active tree"""
        self.controls.notetabs.switch_tree(self)

    def on_button_press(self, w, e):
        if is_double_left_click(e):
            self.active_current_song()
        if is_rigth_click(e):
            menu = Popup()
            menu.add_item('Add to DM', gtk.STOCK_ADD, self.controls.dm.add_beans, self.get_all_selected_beans())
            menu.show(e)
