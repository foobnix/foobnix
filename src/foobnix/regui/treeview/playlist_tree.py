#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
import logging
from foobnix.util import const
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click_release, \
    is_rigth_click
from foobnix.helpers.menu import Popup
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.key_utils import KEY_RETURN, is_key, KEY_DELETE
from foobnix.util.fc import FC
from foobnix.util.tag_util import edit_tags
from foobnix.util.file_utils import open_in_filemanager

class PlaylistTreeControl(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        #self.set_headers_visible(True)
        """Column icon"""
        icon = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), stock_id=self.play_icon[0])
        icon.set_fixed_width(5)
        icon.set_min_width(5)
        self.append_column(icon)
        
        """track number"""
        tracknumber = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.tracknumber[0])
        self.append_column(tracknumber)

        """column artist title"""
        description = gtk.TreeViewColumn('Track', gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        #description.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        description.set_expand(True)
        self.append_column(description)
        
        
        """column artist (NOT USED)"""
        artist = gtk.TreeViewColumn('Artist', gtk.CellRendererText(), text=self.artist[0])
        artist.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        #self.append_column(artist)
        
        """column title (NOT USED)"""
        title = gtk.TreeViewColumn('Title', gtk.CellRendererText(), text=self.title[0])
        title.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        #self.append_column(title)

        """column time"""
        time = gtk.TreeViewColumn('Time', gtk.CellRendererText(), text=self.time[0])
        
        self.append_column(time)

        self.configure_send_drug()
        self.configure_recive_drug()
        
        self.set_playlist_plain()
        
        self.connect("button-release-event", self.on_button_release)
                     
    def set_playlist_tree(self):
        self.rebuild_as_tree()
        
    def set_playlist_plain(self):
        self.rebuild_as_plain()
        
    def on_key_release(self, w, e):
        if is_key(e, KEY_RETURN):
            self.controls.play_selected_song()
        elif is_key(e, KEY_DELETE):
            self.delete_selected()     
        elif is_key(e, 'Left'):
            self.controls.seek_down()
        elif is_key(e, 'Right'):
            self.controls.seek_up()
    
    def common_single_random(self):
        logging.debug("Repeat state" + str(FC().repeat_state))
        if FC().repeat_state == const.REPEAT_SINGLE:
            return self.get_current_bean_by_UUID();
        
        if FC().is_order_random:               
            bean = self.get_random_bean()
            self.set_play_icon_to_bean(bean)
            return bean
    
    def next(self):
        bean = self.common_single_random()       
        if bean:
            return bean
    
        bean = self.get_next_bean_by_UUID(FC().repeat_state == const.REPEAT_ALL)
        
        if not bean:
            return
        
        self.set_play_icon_to_bean(bean)
        
        logging.debug("Next bean" + str(bean) + bean.text)
        
        return bean

    def prev(self):
        bean = self.common_single_random()       
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
        if is_rigth_click(e):
            """to avoid unselect all selected items"""
            self.stop_emission('button-press-event')
        if is_double_left_click(e):
            self.controls.play_selected_song()
            
    def on_button_release(self, w, e):
        if is_rigth_click_release(e):
            """to select item under cursor"""
            try:
                path, col, cellx, celly = self.get_path_at_pos(int(e.x), int(e.y))
                self.get_selection().select_path(path)
            except TypeError:
                pass
                                                               
            menu = Popup()
            menu.add_item(_('Play'), gtk.STOCK_MEDIA_PLAY, self.controls.play_selected_song, None)
            menu.add_item(_('Download'), gtk.STOCK_ADD, self.controls.dm.append_tasks, self.get_all_selected_beans())
            #menu.add_item('Save as', gtk.STOCK_SAVE_AS, self.controls.save_beans_to, self.get_all_selected_beans())
            menu.add_separator()
            try:
                paths = [bean.path for bean in self.get_selected_beans()]
                menu.add_item(_('Edit tags'), gtk.STOCK_EDIT, edit_tags, paths)
                text = self.get_selected_bean().text
                menu.add_item(_('Copy to Search Line'), gtk.STOCK_COPY, self.controls.searchPanel.set_search_text, text)
                menu.add_separator()
            except (TypeError, AttributeError, UnboundLocalError):
                pass
                        
            menu.add_item(_('Copy №-Title-Time'), gtk.STOCK_COPY, self.copy_info_to_clipboard)
            menu.add_item(_('Copy Artist-Title-Album'), gtk.STOCK_COPY, self.copy_info_to_clipboard, True)
            
            menu.add_separator()
            menu.add_item(_('Love this track(s)'), None, self.controls.love_this_tracks, self.get_all_selected_beans())
            try:
                menu.add_separator()
                menu.add_item(_("Open in file manager"), None, open_in_filemanager, self.get_selected_bean().path)
            except:
                pass
            menu.show(e)
