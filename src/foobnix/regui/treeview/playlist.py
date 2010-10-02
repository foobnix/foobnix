#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
from foobnix.regui.treeview import TreeViewControl
import gtk
from foobnix.util.mouse_utils import is_double_left_click
from foobnix.cue.cue_reader import CueReader
from foobnix.regui.model import FModel
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

        self.index = 0
        
        list = []
        list.append(FModel("Madonna").add_font("bold"))
        list.append(FModel("Madonna - Song1").add_font("normal").add_parent("Madonna"))
        list.append(FModel("Madonna - Song2").add_font("normal").add_parent("Madonna"))
        for line in list:
            self.append(line)
        
        #self.set_grid_lines(True)
        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example1", 0, 0)], gtk.gdk.ACTION_COPY)
        self.enable_model_drag_dest([("example1", 0, 0)], gtk.gdk.ACTION_COPY)
        
        self.connect("drag-data-received", self.drag_data_received_data)
        self.connect("drag-data-get", self.drag_data_received_get)
        self.connect("drag-drop", self.on_drag_drop)
    
    def on_drag_drop(self, treeview, drag_context, x, y, selection):
        print "on_drag_drop"
        print treeview, drag_context, x, y, selection
        control = drag_context.get_source_widget()
        bean = control.get_selected_bean()
        print "get_source_widget",
        self.controls.append_to_current_notebook([bean])
         

    def drag_data_received_get(self, *a):
        print "drag_data_received_get"
        print a
         
    def drag_data_received_data(self, treeview, drag_context, x, y, selection, info, eventtime):
        print treeview, drag_context, x, y, selection, info, eventtime
        
        

    def on_key_release(self, w, e):
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
        if self.index < 0:
            self.index = self.count_index - 1
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
        self.controls.notetabs.switch_tree(self)

    def on_button_press(self, w, e):
        if is_double_left_click(e):
            self.active_current_song()

