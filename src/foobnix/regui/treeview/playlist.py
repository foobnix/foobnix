#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.treeview import TreeViewControl
import gtk
from foobnix.util.mouse_utils import is_double_left_click
from foobnix.cue.cue_reader import CueReader
class PlaylistControl(TreeViewControl):
    def __init__(self, controls):
        TreeViewControl.__init__(self, controls)
        self.set_reorderable(True)

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

        self.index = 0

    def on_key_release(self, w,e):
        if gtk.gdk.keyval_name(e.keyval) == 'Return':
            self.active_current_song()

    def next(self):
        #TODO from config use Repeat state
        #if All:
        #    if Linear:
        self.index += 1
        if self.index == self.count_index:
            self.index = 0
        #if Single:
        #    pass
        #if Disable:
        #    return None
        self.repopulate(self.index)
        return self.get_bean_by_position(self.index)

    def prev(self):
        #TODO from config use Repeat state
        #if All:
        #    if Linear:
        self.index -= 1
        if self.index<0:
            self.index = self.count_index-1
        #if Single:
        #    pass
        #if Disable:
        #    return None
        self.repopulate(self.index)
        return self.get_bean_by_position(self.index)

    def append(self, bean):
        if bean.path and bean.path.endswith(".cue"):
            reader = CueReader(bean.path)
            beans = reader.get_common_beans()
            for bean in beans:
                super(PlaylistControl, self).append(bean)
        else:
            return super(PlaylistControl, self).append(bean)

    def repopulate(self, index):
        self.count_index = 0
        all = self.get_all_beans()
        beans = []
        for bean in all:
            print "REPOP", bean
            if bean.index == index:
                bean.play_icon = gtk.STOCK_MEDIA_PLAY
            else:
                bean.play_icon = None
            beans.append(bean)
        self.populate(beans)

    def active_current_song(self):
        current = self.get_selected_bean()
        self.index = current.index
        self.repopulate(current.index)

        """play song"""
        self.controls.play(current)

        """update song info"""
        self.controls.update_info_panel(current)

        """set active tree"""
        self.controls.notetabs.active_tree = self

    def on_button_press(self, w, e):
        if is_double_left_click(e):
            self.active_current_song()

