#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''

import re
import gtk
import logging

from foobnix.fc.fc import FC
from foobnix.util import const
from foobnix.helpers.menu import Popup
from foobnix.util.tag_util import edit_tags
from foobnix.util.converter import convert_files
from foobnix.util.audio import get_mutagen_audio
from foobnix.util.file_utils import open_in_filemanager
from foobnix.util.localization import foobnix_localization
from foobnix.regui.treeview.common_tree import CommonTreeControl
from foobnix.util.key_utils import KEY_RETURN, is_key, KEY_DELETE
from foobnix.util.mouse_utils import is_double_left_click, is_rigth_click_release, \
    is_rigth_click

foobnix_localization()

FLAG = False

class PlaylistTreeControl(CommonTreeControl):
    
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)
        
        self.set_headers_visible(True)
        self.set_headers_clickable(True)
        self.set_reorderable(True)
        
        self.menu = Popup()

        """Column icon"""
        self.icon_col = gtk.TreeViewColumn(None, gtk.CellRendererPixbuf(), stock_id=self.play_icon[0])
        self.icon_col.key = "*"
        self.icon_col.set_fixed_width(5)
        self.icon_col.set_min_width(5)
        self.icon_col.label = gtk.Label("*")
        self._append_column(self.icon_col)
        
        """track number"""
        self.trkn_col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.tracknumber[0])
        self.trkn_col.key = "№"
        self.trkn_col.set_clickable(True)
        self.trkn_col.label = gtk.Label("№")
        self.trkn_col.label.show()
        self.trkn_col.item = gtk.CheckMenuItem(_("Number"))
        self.trkn_col.set_widget(self.trkn_col.label)
        self._append_column(self.trkn_col)
        
        """column composer"""
        self.comp_col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.composer[0])
        self.comp_col.key = "Composer"
        self.comp_col.set_resizable(True)
        self.comp_col.label = gtk.Label(_("Composer"))
        self.comp_col.item = gtk.CheckMenuItem(_("Composer"))
        self._append_column(self.comp_col)
        
        """column artist title"""
        self.description_col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.text[0], font=self.font[0])
        self.description_col.key = "Track"
        self.description_col.set_resizable(True)
        self.description_col.label = gtk.Label(_("Track"))
        self.description_col.item = gtk.CheckMenuItem(_("Track"))
        self._append_column(self.description_col)
                        
        """column artist"""
        self.artist_col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.artist[0])
        self.artist_col.key = "Artist"
        self.artist_col.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.artist_col.set_resizable(True)
        self.artist_col.label = gtk.Label(_("Artist"))
        self.artist_col.item = gtk.CheckMenuItem(_("Artist"))
        self._append_column(self.artist_col)
               
        """column title"""
        self.title_col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.title[0])
        self.title_col.key = "Title"
        self.title_col.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.title_col.set_resizable(True)
        self.title_col.label = gtk.Label(_("Title"))
        self.title_col.item = gtk.CheckMenuItem(_("Title"))
        self._append_column(self.title_col)
        
        """column album"""
        self.album_col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.album[0])
        self.album_col.key = "Album"
        
        
        if not FC().columns.has_key(self.album_col.key):
            FC().columns[self.album_col.key] = [False, 7, 90]
        self.album_col.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.album_col.set_resizable(True)
        self.album_col.label = gtk.Label(_("Album"))
        self.album_col.item = gtk.CheckMenuItem(_("Album"))
        self._append_column(self.album_col)
        
        """column time"""
        self.time_col = gtk.TreeViewColumn(None, gtk.CellRendererText(), text=self.time[0])
        self.time_col.key = "Time"
        self.time_col.label = gtk.Label(_("Time"))
        self.time_col.item = gtk.CheckMenuItem(_("Time"))
        self._append_column(self.time_col)

        self.configure_send_drag()
        self.configure_recive_drag()
        
        self.set_playlist_plain()
        
        self.connect("button-release-event", self.on_button_release)
        
        self.on_load()
        
        self.connect("columns-changed", self.on_columns_changed)
        
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
    
    def get_bean_under_pointer_icon(self):
        for row in self.model:
            if row[self.play_icon[0]]:
                bean = self.get_bean_from_row(row)
                return bean
            
            
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
            self.scroll_follow_play_icon()  
            return bean
        
        bean = self.get_next_bean(FC().repeat_state == const.REPEAT_ALL)
        
        if not bean:
            return
        
        self.set_play_icon_to_bean(bean)
           
        self.scroll_follow_play_icon()            
        
        logging.debug("Next bean" + str(bean) + bean.text)
        
        return bean

    def prev(self):
        bean = self.common_single_random()       
        if bean:
            return bean
    
        bean = self.get_prev_bean(FC().repeat_state == const.REPEAT_ALL)
        
        if not bean:
            return
                
        self.set_play_icon_to_bean(bean)
        
        self.scroll_follow_play_icon() 
        
        return bean
    
    def scroll_follow_play_icon(self):
        paths = [(i,) for i, row in enumerate(self.model)]
        for row, path in zip(self.model, paths):
            if row[self.play_icon[0]]:
                start_path, end_path = self.get_visible_range()
                if path > end_path or path < start_path:
                    self.scroll_to_cell(path)
    
    def append(self, bean):
        return super(PlaylistTreeControl, self).append(bean)

    def on_button_press(self, w, e):
        #self.controls.notetabs.set_active_tree(self)
        if is_rigth_click(e):
            """to avoid unselect all selected items"""
            self.stop_emission('button-press-event')
        if is_double_left_click(e):
            self.controls.play_selected_song()
            
    def on_button_release(self, w, e):
        if is_rigth_click_release(e):
            """to select item under cursor"""
            try:
                path, col, cellx, celly = self.get_path_at_pos(int(e.x), int(e.y)) #@UnusedVariable
                self.get_selection().select_path(path)
            except TypeError:
                pass
            #menu.add_item('Save as', gtk.STOCK_SAVE_AS, self.controls.save_beans_to, self.get_all_selected_beans())
            
            beans = self.get_selected_beans()
            
            if beans:
                menu = Popup()
                menu.add_item(_('Play'), gtk.STOCK_MEDIA_PLAY, self.controls.play_selected_song, None)
                menu.add_item(_('Download'), gtk.STOCK_ADD, self.controls.dm.append_tasks, self.get_all_selected_beans())
                menu.add_item(_('Download To...'), gtk.STOCK_ADD, self.controls.dm.append_tasks_with_dialog, self.get_all_selected_beans())
                menu.add_separator()
                paths = [bean.path for bean in beans]
                if paths[0]:
                    menu.add_item(_('Edit Tags'), gtk.STOCK_EDIT, edit_tags, (self.controls, paths))
                    menu.add_item(_('Format Converter'), gtk.STOCK_CONVERT, convert_files, paths)
                text = self.get_selected_bean().text
                menu.add_item(_('Copy To Search Line'), gtk.STOCK_COPY, self.controls.searchPanel.set_search_text, text)
                menu.add_separator()
                menu.add_item(_('Copy №-Title-Time'), gtk.STOCK_COPY, self.copy_info_to_clipboard)
                menu.add_item(_('Copy Artist-Title-Album'), gtk.STOCK_COPY, self.copy_info_to_clipboard, True)
                menu.add_separator()
                menu.add_item(_('Love This Track(s)'), None, self.controls.love_this_tracks, self.get_all_selected_beans())
                menu.add_separator()
                if paths[0]:
                    menu.add_item(_("Open In File Manager"), None, open_in_filemanager, paths[0])
                menu.show(e)
            
    def on_click_header(self, w, e):
        if is_rigth_click(e):
            if w.__dict__.has_key("menu"):
                w.menu.show(e)
            else:
                self.menu.show(e)
            
    def on_toggled_num(self, *a):
        FC().numbering_by_order = not FC().numbering_by_order
        number_music_tabs = self.controls.notetabs.get_n_pages() - 1
        for page in xrange(number_music_tabs, 0, -1):
            tab_content = self.controls.notetabs.get_nth_page(page)
            pl_tree = tab_content.get_child()
            if FC().numbering_by_order:
                pl_tree.rebuild_as_plain()
                pl_tree.num_order.set_active(True)
                continue
            pl_tree.num_tags.set_active(True)
            for row in pl_tree.model:
                if row[pl_tree.is_file[0]]:
                    audio = get_mutagen_audio(row[pl_tree.path[0]])
                    if audio and audio.has_key('tracknumber'):
                        row[pl_tree.tracknumber[0]] = re.search('\d*', audio['tracknumber'][0]).group()
                    if audio and audio.has_key('trkn'):
                        row[pl_tree.tracknumber[0]] = re.search('\d*', audio["trkn"][0]).group()
        
    def on_toggle(self, w, e, column):
        FC().columns[column.key][0] = not FC().columns[column.key][0]
        
        number_music_tabs = self.controls.notetabs.get_n_pages() - 1
        for key in self.__dict__.keys():
            if self.__dict__[key] is column:
                atr_name = key
                break
        for page in xrange(number_music_tabs, 0, -1):
            tab_content = self.controls.notetabs.get_nth_page(page)
            pl_tree = tab_content.get_child()
            pl_tree_column = pl_tree.__dict__[atr_name]
            if FC().columns[column.key][0]:
                pl_tree.move_column_after(pl_tree_column, pl_tree.icon_col)
                pl_tree_column.set_visible(True)
                if self is not pl_tree:
                    pl_tree_column.item.set_active(True)
            else:
                pl_tree_column.set_visible(False)
                if self is not pl_tree:
                    pl_tree_column.item.set_active(False)
    
    def _append_column(self, column):
        column.set_widget(column.label)
        column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        if column.key in ['*', '№', 'Time']:
            column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        else:
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
        if FC().columns[column.key][2] > 0:
            column.set_fixed_width(FC().columns[column.key][2])
        
        self.append_column(column)
        column.button = column.label.get_parent().get_parent().get_parent()
        column.button.connect("button-press-event", self.on_click_header)
        if column.key == '№':
            self.trkn_col.button.menu = Popup()
            self.num_order = gtk.RadioMenuItem(None, _("Numbering by order"))
            self.num_order.connect("button-press-event", self.on_toggled_num)
            self.num_tags = gtk.RadioMenuItem(self.num_order, _("Numbering by tags"))
            self.num_tags.connect("button-press-event", self.on_toggled_num)
        
            self.trkn_col.button.menu.append(self.num_order)
            self.trkn_col.button.menu.append(self.num_tags)
            if FC().numbering_by_order:
                self.num_order.set_active(True)
            else:
                self.num_tags.set_active(True)
    
    def on_columns_changed(self, *a):
        global FLAG
        if FLAG:
            return
        FLAG = True 
        
        number_music_tabs = self.controls.notetabs.get_n_pages() - 1
        for i, column in enumerate(self.get_columns()):
            FC().columns[column.key][1] = i
            if column.get_width() > 1: #to avoid recording of zero width in config 
                FC().columns[column.key][2] = column.get_width()
        
        for page in xrange(number_music_tabs, 0, -1):
            tab_content = self.controls.notetabs.get_nth_page(page)
            pl_tree = tab_content.get_child()
            col_list = pl_tree.get_columns()
            col_list.sort(self.to_order_columns, reverse=True)
            for column in col_list:
                pl_tree.move_column_after(column, None)
        FLAG = False
        
    def to_order_columns(self, x, y):
        return cmp(FC().columns[x.key][1], FC().columns[y.key][1])  
                          
    def on_load(self):
        col_list = self.get_columns()
        col_list.sort(self.to_order_columns, reverse=True)
        visible_columns = []
        for column in col_list:
            column.label.show()
            column.set_widget(column.label)
            column.set_clickable(True)
            if column.key != "*":
                column.set_reorderable(True)            
            if FC().columns[column.key][0]:
                self.move_column_after(column, None)
                if column.__dict__.has_key("item"):
                    column.item.connect("button-press-event", self.on_toggle, column)
                    self.menu.append(column.item)
                    column.item.set_active(True)
                visible_columns.append(column)
            else:
                if column.__dict__.has_key("item"):
                    column.item.connect("button-press-event", self.on_toggle, column)
                    self.menu.append(column.item)
                    column.item.set_active(False)
                column.set_visible(False)
        '''if FC().columns["Track"][2] < 0:
             self.description_col.set_fixed_width(self.get_allocation().width - (FC().columns["Time"][2]+70))'''