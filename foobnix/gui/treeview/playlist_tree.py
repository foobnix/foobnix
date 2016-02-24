#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''


import logging
import os
import re
import thread

from gi.repository import GLib
from gi.repository import Gtk

from foobnix.fc.fc import FC
from foobnix.gui.treeview.common_tree import CommonTreeControl
from foobnix.helpers.menu import Popup
from foobnix.playlists.m3u_reader import update_id3_for_m3u
from foobnix.playlists.pls_reader import update_id3_for_pls
from foobnix.util import const, idle_task
from foobnix.util.audio import get_mutagen_audio
from foobnix.util.bean_utils import get_bean_from_file
from foobnix.util.converter import convert_files
from foobnix.util.file_utils import open_in_filemanager, copy_to, get_files_from_gtk_selection_data,\
    get_file_extension, is_playlist
from foobnix.util.id3_util import update_id3
from foobnix.util.key_utils import KEY_RETURN, is_key, KEY_DELETE, \
    is_modificator
from foobnix.util.localization import foobnix_localization
from foobnix.util.mouse_utils import is_double_left_click, \
    is_rigth_click, right_click_optimization_for_trees, is_empty_click
from foobnix.util.tag_util import edit_tags


foobnix_localization()

FLAG = False


class PlaylistTreeControl(CommonTreeControl):
    def __init__(self, controls):
        CommonTreeControl.__init__(self, controls)

        self.header_pressed = False

        self.menu = Popup()
        self.tree_menu = Popup()
        self.full_name = ""
        self.label = Gtk.Label.new(None)

        self.set_headers_visible(True)
        self.set_headers_clickable(True)
        self.set_reorderable(True)

        """Column icon"""
        self.icon_col = Gtk.TreeViewColumn(None, Gtk.CellRendererPixbuf.new(), icon_name=self.play_icon[0])
        self.icon_col.key = "*"
        self.icon_col.label = Gtk.Label.new("*")
        self._append_column(self.icon_col)

        """track number"""
        self.trkn_col = Gtk.TreeViewColumn(None, Gtk.CellRendererText.new(), text=self.tracknumber[0])
        self.trkn_col.key = "N"
        #self.trkn_col.set_clickable(True)
        self.trkn_col.label = Gtk.Label.new("№")
        self.trkn_col.item = Gtk.CheckMenuItem.new_with_label(_("Number"))
        self._append_column(self.trkn_col)

        """column composer"""
        self.comp_col = Gtk.TreeViewColumn(None, self.ellipsize_render, text=self.composer[0])
        self.comp_col.key = "Composer"
        self.comp_col.label = Gtk.Label.new(_("Composer"))
        self.comp_col.item = Gtk.CheckMenuItem.new_with_label(_("Composer"))
        self._append_column(self.comp_col)

        """column artist title"""
        self.description_col = Gtk.TreeViewColumn(None, self.ellipsize_render, text=self.text[0], font=self.font[0])
        self.description_col.key = "Track"
        self.description_col.label = Gtk.Label.new(_("Track"))
        self.description_col.item = Gtk.CheckMenuItem.new_with_label(_("Track"))
        self._append_column(self.description_col)

        """column artist"""
        self.artist_col = Gtk.TreeViewColumn(None, self.ellipsize_render, text=self.artist[0])
        self.artist_col.key = "Artist"
        self.artist_col.label = Gtk.Label.new(_("Artist"))
        self.artist_col.item = Gtk.CheckMenuItem.new_with_label(_("Artist"))
        self._append_column(self.artist_col)

        """column title"""
        self.title_col = Gtk.TreeViewColumn(None, self.ellipsize_render, text=self.title[0])
        self.title_col.key = "Title"
        self.title_col.label = Gtk.Label.new(_("Title"))
        self.title_col.item = Gtk.CheckMenuItem.new_with_label(_("Title"))
        self._append_column(self.title_col)

        """column year"""
        self.year_col = Gtk.TreeViewColumn(None, Gtk.CellRendererText.new(), text=self.year[0])
        self.year_col.key = "Year"
        self.year_col.label = Gtk.Label.new(_("Year"))
        self.year_col.item = Gtk.CheckMenuItem.new_with_label(_("Year"))
        self._append_column(self.year_col)

        """column album"""
        self.album_col = Gtk.TreeViewColumn(None, self.ellipsize_render, text=self.album[0])
        self.album_col.key = "Album"

        if self.album_col.key not in FC().columns:
            FC().columns[self.album_col.key] = [False, 7, 90]
        self.album_col.label = Gtk.Label.new(_("Album"))
        self.album_col.item = Gtk.CheckMenuItem.new_with_label(_("Album"))
        self._append_column(self.album_col)

        """column time"""
        self.time_col = Gtk.TreeViewColumn(None, Gtk.CellRendererText.new(), text=self.time[0])
        self.time_col.key = "Time"
        self.time_col.label = Gtk.Label.new(_("Time"))
        self.time_col.item = Gtk.CheckMenuItem.new_with_label(_("Time"))
        self._append_column(self.time_col)

        self.configure_send_drag()
        self.configure_recive_drag()

        self.set_playlist_plain()

        self.connect("button-release-event", self.on_button_press)
        self.connect("columns-changed", self.on_columns_changed)

        self.on_load()

    def set_playlist_tree(self):
        self.rebuild_as_tree()

    def set_playlist_plain(self):
        self.rebuild_as_plain()

    def on_key_release(self, w, e):
        if is_modificator(e):
            return
        elif is_key(e, KEY_RETURN):
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
        logging.debug("Repeat state " + str(FC().repeat_state))
        if FC().repeat_state == const.REPEAT_SINGLE:
            return self.get_current_bean_by_UUID()

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
            self.controls.state_stop()
            return

        self.set_play_icon_to_bean(bean)
        self.scroll_follow_play_icon()

        logging.debug("Next bean " + str(bean) + bean.text)

        return bean

    def prev(self):
        if FC().repeat_state == const.REPEAT_SINGLE:
            return self.get_current_bean_by_UUID()

        bean = self.get_prev_bean(FC().repeat_state == const.REPEAT_ALL)

        if not bean:
            self.controls.state_stop()
            return

        self.set_play_icon_to_bean(bean)
        self.scroll_follow_play_icon()

        return bean

    @idle_task
    def scroll_follow_play_icon(self):
        paths = [(i,) for i, row in enumerate(self.model)]
        for row, path in zip(self.model, paths):
            if row[self.play_icon[0]]:
                start_path, end_path = self.get_visible_range()
                path = row.path
                if path >= end_path or path <= start_path:
                    self.scroll_to_cell(path)

    def append(self, paths):
        for i, path in enumerate(paths):
            if os.path.isdir(path):
                listdir = filter(lambda x: get_file_extension(x) in FC().all_support_formats or os.path.isdir(x),
                                 [os.path.join(path, f) for f in os.listdir(path)])
                for k, p in enumerate(listdir):
                    paths.insert(i + k + 1, p)
        rows = self.file_paths_to_rows(paths)
        if not rows:
            return
        #rows = self.playlist_filter(rows)
        for row in rows:
            self.model.append(None, row)
        thread.start_new_thread(self.safe_fill_treerows, ())

    def is_empty(self):
        return True if not self.model.get_iter_first() else False

    def on_button_press(self, w, e):
        if self.header_pressed:
            self.header_pressed = False
            return
        if is_empty_click(w, e):
            w.get_selection().unselect_all()
        if is_double_left_click(e):
            self.controls.play_selected_song()

        if is_rigth_click(e):
            right_click_optimization_for_trees(w, e)
            beans = self.get_selected_beans()
            if beans:
                self.tree_menu.clear()
                self.tree_menu.add_item(_('Play'), "media-playback-start", self.controls.play_selected_song, None)
                self.tree_menu.add_item(_('Delete from playlist'), "edit-delete", self.delete_selected, None)

                paths = []
                inet_paths = []
                local_paths = []
                for bean in beans:
                    if bean.path in paths:
                        continue
                    paths.append(bean.path)
                    if not bean.path or bean.path.startswith("http://"):
                        inet_paths.append(bean.path)
                    else:
                        local_paths.append(bean.path)

                if local_paths:
                    self.tree_menu.add_item(_('Copy To...'), "list-add", copy_to, local_paths)
                    self.tree_menu.add_item(_("Open in file manager"), "system-file-manager", open_in_filemanager, local_paths[0])
                if inet_paths:
                    self.tree_menu.add_item(_('Download'), "download",
                                            self.controls.dm.append_tasks, self.get_all_selected_beans())
                    self.tree_menu.add_item(_('Download To...'), "folder-downloads",
                                            self.controls.dm.append_tasks_with_dialog, self.get_all_selected_beans())

                self.tree_menu.add_separator()

                if local_paths:
                    self.tree_menu.add_item(_('Edit Tags'), "accessories-text-editor", edit_tags, (self.controls, local_paths))
                    self.tree_menu.add_item(_('Format Converter'), "convertimages", convert_files, local_paths)
                text = self.get_selected_bean().text
                self.tree_menu.add_item(_('Copy To Search Line'), "system-search",
                                        self.controls.searchPanel.set_search_text, text)
                self.tree_menu.add_separator()
                self.tree_menu.add_item(_('Copy link'), "insert-link",
                                        self.controls.copy_link, self.get_all_selected_beans())
                self.tree_menu.add_item(_('Copy №-Title-Time'), "edit-copy", self.copy_info_to_clipboard)
                self.tree_menu.add_item(_('Copy Artist-Title-Album'), "edit-copy",
                                        self.copy_info_to_clipboard, True)
                self.tree_menu.add_separator()
                self.tree_menu.add_item(_('Add to My Audio (VK)'), "list-add",
                                        self.controls.add_to_my_playlist, self.get_all_selected_beans())
                self.tree_menu.add_item(_('Love This Track(s) by Last.fm'), "heart",
                                        self.controls.love_this_tracks, self.get_all_selected_beans())

                self.tree_menu.show(e)

    def on_click_header(self, w, e):
        self.header_pressed = True
        if is_rigth_click(e):
            if "menu" in w.__dict__:
                w.menu.show(e)
            else:
                self.menu.show(e)

    def on_toggled_num(self, *a):
        FC().numbering_by_order = not FC().numbering_by_order
        number_music_tabs = self.controls.notetabs.get_n_pages() - 1
        for page in xrange(number_music_tabs, -1, -1):
            tab_content = self.controls.notetabs.get_nth_page(page)
            pl_tree = tab_content.get_child()
            if FC().numbering_by_order:
                pl_tree.update_tracknumber()
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

        for page in xrange(number_music_tabs, -1, -1):
            tab_content = self.controls.notetabs.get_nth_page(page)
            pl_tree = tab_content.get_child()
            ## TODO: check "local variable 'atr_name' might be referenced before assignment"
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
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.set_min_width(20)
        column.set_resizable(True)
        if column.key is '*':
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
            column.set_fixed_width(32)
            column.set_min_width(32)
        try:
            if FC().columns[column.key][2] > 0:
                column.set_fixed_width(FC().columns[column.key][2])
        except KeyError:
            column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)

        self.append_column(column)
        column.button = column.label.get_parent().get_parent().get_parent()
        column.button.connect("button-press-event", self.on_click_header)
        '''
        if column.key == 'N':
            self.trkn_col.button.menu = Popup()
            group = []
            self.num_order = Gtk.RadioMenuItem.new_with_label(group, _("Numbering by order"))
            self.num_order.connect("button-press-event", self.on_toggled_num)
            group.append(self.num_order)
            self.num_tags = Gtk.RadioMenuItem.new_with_label(group, _("Numbering by tags"))
            self.num_tags.connect("button-press-event", self.on_toggled_num)
            group.append(self.num_tags)
            self.trkn_col.button.menu.append(self.num_order)
            self.trkn_col.button.menu.append(self.num_tags)
            if FC().numbering_by_order:
                self.num_order.set_active(True)
            else:
                self.num_tags.set_active(True)
        '''

    def on_columns_changed(self, *a):
        global FLAG
        if FLAG:
            return
        FLAG = True

        number_music_tabs = self.controls.notetabs.get_n_pages() - 1
        for i, column in enumerate(self.get_columns()):
            try:
                FC().columns[column.key][1] = i
            except KeyError:
                FC().columns[column.key] = [column.get_visible(), i, 80]
            if column.get_width() > 1:  # to avoid recording of zero width in config
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
        try:
            return cmp(FC().columns[x.key][1], FC().columns[y.key][1])
        except KeyError:
            return -1

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
            try:
                visible = FC().columns[column.key][0]
            except KeyError:
                visible = False
            if visible:
                self.move_column_after(column, None)
                if "item" in column.__dict__:
                    column.item.connect("button-press-event", self.on_toggle, column)
                    self.menu.append(column.item)
                    column.item.set_active(True)
                visible_columns.append(column)
            else:
                if "item" in column.__dict__:
                    column.item.connect("button-press-event", self.on_toggle, column)
                    self.menu.append(column.item)
                    column.item.set_active(False)
                column.set_visible(False)
        '''if FC().columns["Track"][2] < 0:
             self.description_col.set_fixed_width(self.get_allocation().width - (FC().columns["Time"][2]+70))'''

    def change_rows_by_path(self, file_paths):
        for treerow in self.model:
            if treerow[self.is_file[0]] and treerow[self.path[0]] in file_paths:
                bean = self.get_bean_from_row(treerow)
                bean = update_id3(bean)
                row_ref = Gtk.TreeRowReference.new(self.model, treerow.path)
                self.fill_row(row_ref, bean)
        GLib.idle_add(self.controls.notetabs.save_current_tab, priority=GLib.PRIORITY_LOW)

    def file_paths_to_rows(self, paths):
        result = []
        for path in paths:
            bean = get_bean_from_file(path)
            beans = update_id3_for_m3u([bean])
            beans = update_id3_for_pls(beans)
            if beans and (len(beans) > 1 or is_playlist(bean.path)):
                    bean = bean.add_text(_('Playlist: ') + bean.text).add_font("bold").add_is_file(False)
                    bean.path = ''
                    beans.insert(0, bean)
            for bean in beans:
                result.append(self.get_row_from_bean(bean))
        return result

    def on_drag_data_received(self, treeview, context, x, y, selection, info, timestamp):
        logging.debug('Playlist on_drag_data_received')
        model = self.get_model().get_model()
        drop_info = self.get_dest_row_at_pos(x, y)

        if drop_info:
            path, position = drop_info
            iter = model.get_iter(path)

        files = sorted([file for file in get_files_from_gtk_selection_data(selection)
                if os.path.isdir(file) or get_file_extension(file) in FC().all_support_formats],
                key=lambda x: x[self.text[0]])
        if files:
            '''dnd from the outside of the player'''
            if self.is_empty():
                if len(files) == 1 and os.path.isdir(files[0]):
                    tabname = os.path.basename(files[0])
                else:
                    tabname = os.path.split(os.path.dirname(files[0]))[1]
                self.controls.notetabs.rename_tab(self.scroll, tabname)
            for i, file in enumerate(files):
                if os.path.isdir(file):
                    sorted_dirs = []
                    sorted_files = []
                    for f in sorted(os.listdir(file), key=lambda x: x):
                        f = os.path.join(file, f)
                        if os.path.isdir(f):
                            sorted_dirs.append(f)
                        elif get_file_extension(f) in FC().all_support_formats:
                            sorted_files.append(f)

                    listdir = sorted_dirs + sorted_files
                    '''
                    listdir = sorted(filter(lambda x: get_file_extension(x) in FC().all_support_formats or os.path.isdir(x),
                                     [os.path.join(file, f) for f in os.listdir(file)]), key=lambda x: x)
                    '''
                    for k, path in enumerate(listdir):
                        files.insert(i + k + 1, path)

            rows = self.file_paths_to_rows(files)
            if not rows:
                return
            rows = self.playlist_filter(rows)
            for row in rows:
                if drop_info:
                    if (position == Gtk.TreeViewDropPosition.BEFORE
                        or position == Gtk.TreeViewDropPosition.INTO_OR_BEFORE):
                        model.insert_before(None, iter, row)
                    else:
                        model.insert_after(None, iter, row)
                        iter = model.iter_next(iter)
                else:
                    model.append(None, row)

        else:
            '''dnd inside the player'''
            # ff - from_filter
            ff_tree = Gtk.drag_get_source_widget(context)
            ff_model, ff_paths = ff_tree.get_selection().get_selected_rows()
            treerows = [ff_model[ff_path] for ff_path in ff_paths]

            if self is ff_tree:
                '''internal dnd'''
                ff_row_refs = [Gtk.TreeRowReference.new(ff_model, ff_path) for ff_path in ff_paths]
                for ff_row_ref in ff_row_refs:
                    ff_iter = self.get_iter_from_row_reference(ff_row_ref)
                    f_iter = ff_model.convert_iter_to_child_iter(ff_iter)
                    if drop_info:
                        if (position == Gtk.TreeViewDropPosition.BEFORE
                            or position == Gtk.TreeViewDropPosition.INTO_OR_BEFORE):
                            model.move_before(f_iter, iter)
                        else:
                            model.move_after(f_iter, iter)
                            iter = model.iter_next(iter)
                    else:
                        model.move_before(f_iter, None)
                return

            else:
                '''dnd from other tree'''
                if self.is_empty():
                    path = treerows[0][self.path[0]]
                    if path:
                        if len(treerows) == 1 and os.path.isdir(path):
                            tabname = os.path.basename(path)
                        else:
                            tabname = os.path.split(os.path.dirname(path))[1]
                        self.controls.notetabs.rename_tab(self.scroll, tabname)
                    else:
                        pass
                for i, treerow in enumerate(treerows):

                    for k, ch_row in enumerate(treerow.iterchildren()):
                        treerows.insert(i + k + 1, ch_row)

                #treerows = self.playlist_filter(treerows)

                for i, treerow in enumerate(treerows):
                    if is_playlist(treerow[self.path[0]]):
                        rows = self.file_paths_to_rows([treerow[self.path[0]]])
                        if rows:
                            rows.reverse()
                            map(lambda row: treerows.insert(i + 1, row), rows)
                            continue
                    row = [col for col in treerow]
                    if drop_info:
                        if (position == Gtk.TreeViewDropPosition.BEFORE
                            or position == Gtk.TreeViewDropPosition.INTO_OR_BEFORE):
                            model.insert_before(None, iter, row)
                        else:
                            model.insert_after(None, iter, row)
                            iter = model.iter_next(iter)
                    else:
                        model.append(None, row)


        thread.start_new_thread(self.safe_fill_treerows, ())

        context.finish(True, False, timestamp)
        self.stop_emission('drag-data-received')
        return True

