'''
Created on Oct 14, 2010

@author: ivan
'''

from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gtk

import copy
import thread
import logging
import os.path
import threading
import collections

from foobnix.gui.model import FModel, FTreeModel, FDModel
from foobnix.util.file_utils import get_file_extension, is_m3u
from foobnix.util.id3_file import update_id3_wind_filtering
from foobnix.util.iso_util import get_beans_from_iso_wv
from foobnix.util import idle_task_priority, idle_task

try:
    from gi.repository.GLib import GError
except ImportError as e:
    try:
        from gi._glib import GError
    except ImportError as e:
        from gi._glib._glib import GError

VIEW_PLAIN = 0
VIEW_TREE = 1

class DragDropTree(Gtk.TreeView):
    def __init__(self, controls):
        self.controls = controls
        Gtk.TreeView.__init__(self)

        self.connect("drag-begin", self.on_drag_begin)
        self.connect("drag-data-get", self.on_drag_data_get)
        self.connect("drag-data-received", self.on_drag_data_received)
        self.connect("drag-drop", self.on_drag_drop)
        self.connect("drag-motion", self.on_drag_motion)
        self.connect('drag-leave', self.on_drag_leave)
        self.connect('drag-end', self.on_drag_end)

        """init values"""
        self.hash = {None: None}
        self.current_view = None
        self.filling_lock = threading.Lock()

    def on_drag_data_get(self, source_tree, drag_context, selection, info, time):
        pass

    def on_drag_end(self, *a):
        pass

    def on_drag_data_received(self, treeview, context, x, y, selection, info, timestamp):
        self.stop_emission('drag-data-received')

    def on_drag_begin(self, source_widget, drag_context):
        ff_model, ff_paths = source_widget.get_selection().get_selected_rows()  # @UnusedVariable
        if len(ff_paths) > 1:
            self.drag_source_set_icon_stock('gtk-dnd-multiple')
        else:
            self.drag_source_set_icon_stock('gtk-dnd')

    def on_drag_motion(self, widget, drag_context, x, y, time):
        Gdk.drag_status(drag_context, Gdk.DragAction.COPY, time)
        widget.drag_highlight()
        drop_info = widget.get_dest_row_at_pos(x, y)
        if drop_info:
            self.set_drag_dest_row(*drop_info)

    def on_drag_leave(self, widget, context, time):
        widget.drag_unhighlight()

    def configure_recive_drag(self):
        self.enable_model_drag_dest([("text/uri-list", 0, 0)], Gdk.DragAction.COPY | Gdk.DragAction.MOVE) # @UndefinedVariable
        self.drag_dest_add_text_targets()

    def configure_send_drag(self):
        self.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [Gtk.TargetEntry.new("text/uri-list", 0, 0)], Gdk.DragAction.COPY | Gdk.DragAction.MOVE) #@UndefinedVariable
        self.drag_source_add_text_targets()

    def append_all(self, beans):
        logging.debug("begin append all")
        if self.current_view == VIEW_PLAIN:
            self.plain_append_all(beans)
        else:
            self.tree_append_all(beans)

    def simple_append_all(self, beans):
        logging.debug("simple_append_all")

        if self.current_view == VIEW_PLAIN:
            for bean in beans:
                row = self.get_row_from_bean(bean)
                self.model.append(None, row)
            if "PlaylistTreeControl" in str(self):
                thread.start_new_thread(self.controls.notetabs.on_save_tabs, ())
        else:
            self.tree_append_all(beans)

    def append(self, bean):
        if self.current_view == VIEW_PLAIN:
            self.plain_append_all([bean])
        else:
            self.tree_append(bean)

    def set_type_plain(self):
        self.current_view = VIEW_PLAIN

    def set_type_tree(self):
        self.current_view = VIEW_TREE

    def get_bean_from_model_iter(self, model, iter):
        if not model or not iter:
            return None
        bean = FModel()
        id_dict = FTreeModel().cut().__dict__
        for key in id_dict.keys():
            num = id_dict[key]
            try:
                val = model.get_value(iter, num)
            except GError:
                val = None
            setattr(bean, key, val)
        return bean

    def on_drag_drop(self, to_tree, context, x, y, time):
        to_tree.drag_get_data(context, context.list_targets()[-1], time)
        return True

    def remove_replaced(self, model, rowrefs):
        for ref in rowrefs:
            iter = self.get_iter_from_row_reference(ref)
            iter = model.convert_iter_to_child_iter(iter)
            model.get_model().remove(iter)

    def child_by_recursion(self, row, plain):
        for child in row.iterchildren():
            plain.append(child)
            self.child_by_recursion(child, plain)

    def rebuild_as_tree(self, *a):
        self.current_view = VIEW_TREE
        plain = []
        for row in self.model:
            plain.append(row)
            self.child_by_recursion(row, plain)

        copy_beans = []
        for row in plain:
            bean = self.get_bean_from_row(row)
            copy_beans.append(bean)

        self.clear_tree()

        self.tree_append_all(copy_beans)

        self.expand_all()

    def rebuild_as_plain(self, with_beans=True):
        self.current_view = VIEW_PLAIN
        if len(self.model) == 0:
            return
        plain = []
        for row in self.model:
            plain.append(row)
            self.child_by_recursion(row, plain)
        if not with_beans:
            for row in plain:
                self.model.append(None, row)
            return
        copy_beans = []
        for row in plain:
            bean = self.get_bean_from_row(row)
            copy_beans.append(bean)

        self.clear_tree()
        self.plain_append_all(copy_beans)

    @idle_task
    def tree_append_all(self, beans):
        self._tree_append_all(beans)

    def _tree_append_all(self, beans):
        if not beans:
            return None
        self.current_view = VIEW_TREE
        logging.debug("append all as tree")

        for bean in beans:
            self.tree_append(bean)

    def get_iter_from_bean(self, bean):
        for row in self.model:
            if row[self.UUID[0]] == bean.UUID:
                return row.iter
        return None

    def remove_iters(self, allIters):
        for iter in allIters:
            self.model.remove(iter)

    def get_child_iters_by_parent(self, model, iter):
        list = []
        if model.iter_has_child(iter):
            for i in xrange(model.iter_n_children(iter)):
                next_iter = model.iter_nth_child(iter, i)

                list.append(next_iter)

                iters = self.get_child_beans_by_parent(model, next_iter)

                for iter in iters:
                    list.append(iter)

        return list

    def get_child_beans_by_parent(self, model, iter):
        list = []

        def add_to_list(beans):
            for i, bean in enumerate(beans):
                if i: bean.parent(parent)
                if bean.path and bean.path.lower().endswith(".iso.wv"):
                    add_to_list(get_beans_from_iso_wv(bean.path))
                else:
                    list.append(bean)

        if model.iter_has_child(iter):
            for i in xrange(model.iter_n_children(iter)):
                next_iter = model.iter_nth_child(iter, i)

                parent = self.get_bean_from_model_iter(model, next_iter)
                add_to_list([parent])

                beans = self.get_child_beans_by_parent(model, next_iter)
                add_to_list(beans)

        return list

    @idle_task
    def plain_append_all(self, beans, parent=None):
        try:
            self._plain_append_all(beans, parent)
        finally:
            if "PlaylistTreeControl" in str(self):
                thread.start_new_thread(self.controls.notetabs.on_save_tabs, ())

    def _plain_append_all(self, beans, parent=None):
        logging.debug("begin plain append all")
        if not beans:
            return

        parent_iter = None
        if parent:
            parent_iter = self.get_iter_from_bean(parent)

        self.current_view = VIEW_PLAIN

        normalized = []
        for model in beans:
            if model.path and model.path.lower().endswith(".iso.wv"):
                logging.debug("begin normalize iso.wv" + str(model.path))
                all = get_beans_from_iso_wv(model.path)

                if not all:
                    break
                for inner in all:
                    normalized.append(inner)
            else:
                normalized.append(model)

        beans = normalized

        #counter = 0
        for bean in beans:
            """if not bean.path or not get_file_extension(bean.path) == ".cue":
                if bean.is_file and FC().numbering_by_order:
                    counter += 1
                    bean.tracknumber = counter
                else:
                    counter = 0
            """
            self._plain_append(bean, parent_iter)

    def _plain_append(self, bean, parent_iter):
        logging.debug("Plain append task: " + str(bean.text) + " " + str(bean.path))
        if not bean:
            return

        if bean.is_file:
            bean.font = "normal"
        else:
            bean.font = "bold"

        bean.visible = True
        beans = update_id3_wind_filtering([bean])
        for one in beans:
            one.update_uuid()
            row = self.get_row_from_bean(one)

            self.model.append(parent_iter, row)

    def tree_append(self, bean):
        if not bean:
            return
        if bean.is_file:
            bean.font = "normal"
        else:
            bean.font = "bold"

        """copy beans"""
        bean = copy.copy(bean)
        bean.visible = True

        last_folder_iter = None

        row = self.get_row_from_bean(bean)

        if self.hash.has_key(bean.get_parent()):
            parent_iter_exists = self.hash[bean.get_parent()]
            if not bean.is_file:
                for i in xrange(self.model.iter_n_children(parent_iter_exists)):
                    iter = self.model.iter_nth_child(parent_iter_exists, i)
                    if not self.model.get_value(iter, self.is_file[0]):
                        last_folder_iter = iter
                if last_folder_iter:
                    new_iter = self.model.insert_after(None, last_folder_iter, row)
                    self.hash[bean.level] = new_iter
                    return
                else:
                    new_iter = self.model.prepend(parent_iter_exists, row)
                    self.hash[bean.level] = new_iter
                    return
        else:
            parent_iter_exists = None

        parent_iter = self.model.append(parent_iter_exists, row)
        self.hash[bean.level] = parent_iter

    def tree_insert_row(self, row):
        last_folder_iter = None

        if self.hash.has_key(row[self.parent_level[0]]):
            parent_iter_exists = self.hash[row[self.parent_level[0]]]
            if not row[self.is_file[0]]:
                for i in xrange(self.model.iter_n_children(parent_iter_exists)):
                    iter = self.model.iter_nth_child(parent_iter_exists, i)
                    if not self.model.get_value(iter, self.is_file[0]):
                        last_folder_iter = iter

                if last_folder_iter:
                    new_iter = self.model.insert_after(None, last_folder_iter, row)
                    self.hash[row[self.level[0]]] = new_iter
                    return
                else:
                    new_iter = self.model.prepend(parent_iter_exists, row)
                    self.hash[row[self.level[0]]] = new_iter
                    return
        else:
            parent_iter_exists = None

        parent_iter = self.model.append(parent_iter_exists, row)
        self.hash[row[self.level[0]]] = parent_iter



    def get_row_from_iter(self, model, iter):
        row = []
        for num in xrange(model.get_n_columns()):
            try:
                val = model.get_value(iter, num)
            except GError:
                val = None
            row.append(val)
        return row

    def get_list_of_iters_with_children(self, model, iter):
        all_iters = []
        def task(iter):
            all_iters.append(iter)
            for n in xrange(model.iter_n_children(iter)):
                child_iter = model.iter_nth_child(iter, n)
                if child_iter:
                    task(child_iter)
        task(iter)
        return all_iters

    def get_list_of_paths_with_children(self, model, iter):
        all_paths = []
        def task(iter):
            path = model.get_path(iter)
            all_paths.append(path)
            for n in xrange(model.iter_n_children(iter)):
                child_iter = model.iter_nth_child(iter, n)
                if child_iter:
                    task(child_iter)
        task(iter)
        return all_paths

    def fill_treerows(self):
        all_extra_rows = {}

        for k, treerow in enumerate(self.model):
            if not treerow[self.time[0]] and treerow[self.is_file[0]]:
                bean = self.get_bean_from_row(treerow)
                full_beans = update_id3_wind_filtering([bean])
                rows_for_add = []
                if len(full_beans) == 1:
                    full_bean = full_beans[0]
                    m_dict = FTreeModel().cut().__dict__
                    new_dict = dict(zip(m_dict.values(), m_dict.keys()))
                    for i, key in enumerate(new_dict.values()):
                        value = getattr(full_bean, key)
                        if value is None:
                            value = ''
                        elif type(value) in [int, float, long]:
                            value = str(value)
                        treerow[i] = value
                else:
                    for n, full_bean in enumerate(full_beans):
                        full_bean.visible = True
                        full_bean.update_uuid()
                        row = self.get_row_from_bean(full_bean)
                        rows_for_add.insert(0, row)
                        if n == 0:
                            treerow[self.font[0]] = 'bold'
                            treerow[self.is_file[0]] = False

                    if rows_for_add:
                        all_extra_rows[k] = rows_for_add

        if all_extra_rows:
            for i in sorted(all_extra_rows.keys(), reverse = True):
                for row in all_extra_rows[i]:
                    self.model.insert_after(None, self.model.get_iter(i), row)

    def safe_fill_treerows(self):
        try:
            self.filling_lock.acquire()

            rows = collections.OrderedDict()
            for treerow in self.model:
                rows[Gtk.TreeRowReference.new(self.model, treerow.path)] = [col for col in treerow]
            for row_ref in rows.keys():
                row = rows[row_ref]
                if not row[self.time[0]] and row[self.is_file[0]] and row_ref.valid():
                    bean = self.get_bean_from_row(row)
                    beans = update_id3_wind_filtering([bean])
                    if len(beans) == 1:
                        self.fill_row(row_ref, beans[:][0])
                    else:
                        bean = FDModel(text=_('Playlist: ') + os.path.basename(bean.path)).add_font("bold").add_is_file(False)
                        self.fill_row(row_ref, bean)
                        beans.reverse()
                        for b in beans[:]:
                            self.insert_bean(row_ref, b)
        finally:
            #self.update_tracknumber()
            self.controls.notetabs.on_save_tabs()
            if self.filling_lock.locked():
                self.filling_lock.release()

    @idle_task_priority(GLib.PRIORITY_LOW)
    def fill_row(self, row_ref, bean):
            if row_ref.valid():
                treerow = self.model[row_ref.get_path()]
                m_dict = FTreeModel().cut().__dict__
                new_dict = dict(zip(m_dict.values(), m_dict.keys()))
                for i, key in enumerate(new_dict.values()):
                    value = getattr(bean, key)
                    if value is None:
                        value = ''
                    elif type(value) in [int, float, long]:
                        value = str(value)
                    if i != self.play_icon[0]:
                        treerow[i] = value

    @idle_task_priority(GLib.PRIORITY_LOW)
    def insert_bean(self, row_ref, bean):
        if row_ref.valid():
            row = self.get_row_from_bean(bean)
            iter = self.model.insert_after(None, self.get_iter_from_row_reference(row_ref), row)
            self.fill_row(self.get_row_reference_from_iter(self.model, iter), bean)
    '''
    @idle_task_priority(GLib.PRIORITY_LOW + 1)
    def update_tracknumber(self):
        try:
            self.current_view = VIEW_PLAIN
            tn = self.tracknumber[0]
            isfile = self.is_file[0]
            counter = 0
            for row in self.model:
                if row[isfile] and FC().numbering_by_order:
                    counter += 1
                else:
                    counter = 0
                row[tn] = str(counter) if counter else ''
        finally:
            self.controls.notetabs.on_save_tabs()
            if self.filling_lock.locked():
                self.filling_lock.release()
    '''

    def playlist_filter(self, rows):
        checked_cue_rows = []
        checked_m3u_rows = []
        m3u_rows_for_delete = []

        def task(rows):
            for row in rows:
                index = self.path[0]
                path = row[index]
                if path and (is_m3u(path)
                             and row not in checked_m3u_rows):
                    checked_m3u_rows.append(row)
                    for r in rows:
                        if (os.path.dirname(r[index]) == os.path.dirname(path) and os.path.isfile(r[index])
                            and not is_m3u(r[index])):
                                m3u_rows_for_delete.append(r)
                                break
                    return task(rows)

                if path and (get_file_extension(path) == ".cue"
                             and row not in checked_cue_rows):

                    checked_cue_rows.append(row)
                    filtered_rows = [r for r in rows if (os.path.dirname(r[index]) != os.path.dirname(path)
                                                           or os.path.isdir(r[index])
                                                           or get_file_extension(r[index]) == ".cue")]
                    return task(filtered_rows)
            return rows

        all_filtered_rows = task(rows)

        return [row for row in all_filtered_rows
                if row not in m3u_rows_for_delete] if m3u_rows_for_delete else all_filtered_rows