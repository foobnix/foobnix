'''
Created on Oct 14, 2010

@author: ivan
'''

from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import Gtk

import copy
import uuid
import thread
import logging
import os.path
import threading

from foobnix.fc.fc import FC
from foobnix.fc.fc_cache import FCache
from foobnix.helpers.dialog_entry import info_dialog
from foobnix.helpers.window import CopyProgressWindow
from foobnix.util.const import BEFORE, AFTER, INTO_OR_BEFORE, INTO_OR_AFTER,\
    FTYPE_RADIO
from foobnix.util.file_utils import copy_move_files_dialog, copy_move_with_progressbar,\
    get_file_extension
from foobnix.util.m3u_utils import m3u_reader, is_m3u
from foobnix.util.id3_file import update_id3_wind_filtering
from foobnix.util.iso_util import get_beans_from_iso_wv
from foobnix.gui.model import FModel, FTreeModel, FDModel
from foobnix.util import idle_task_priority
import collections
from foobnix.playlists.m3u_reader import update_id3_for_m3u
from foobnix.playlists.cue_reader import update_id3_for_cue
## TODO: Check it
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
        self.copy = False

        """init values"""
        self.hash = {None: None}
        self.current_view = None
        self.filling_lock = threading.Lock()

    def on_drag_data_get(self, source_tree, drag_context, selection, info, time):
        pass 

    def on_drag_data_received(self, treeview, context, x, y, selection, info, timestamp):
        self.stop_emission('drag-data-received')
        
    def on_drag_begin(self, source_widget, drag_context):
        ff_model, ff_paths = source_widget.get_selection().get_selected_rows()  # @UnusedVariable
        if len(ff_paths) > 1:
            self.drag_source_set_icon_stock('gtk-dnd-multiple')
        else:
            self.drag_source_set_icon_stock('gtk-dnd')
    
    def on_drag_end(self, *a):
        pass
    
    def on_drag_motion(self, widget, drag_context, x, y, time):
        Gdk.drag_status(drag_context, Gdk.DragAction.COPY, time)
        widget.drag_highlight()
        drop_info = widget.get_dest_row_at_pos(x, y)
        if drop_info:
            self.set_drag_dest_row (*drop_info)
    
    def on_drag_leave(self, widget, context, time):
        widget.drag_unhighlight()
                
    def configure_recive_drag(self):
        self.enable_model_drag_dest([("text/uri-list", 0, 0)], Gdk.DragAction.COPY | Gdk.DragAction.MOVE) # @UndefinedVariable
        self.drag_dest_add_text_targets()
        #self.drag_dest_set(Gtk.DestDefaults.MOTION | Gtk.DestDefaults.DROP, [Gtk.TargetEntry.new("text/uri-list", 1, 80)], Gdk.DragAction.COPY | Gdk.DragAction.MOVE)
    
    def configure_send_drag(self):
        #self.enable_model_drag_source(Gdk.ModifierType.BUTTON1_MASK, [("text/uri-list", 0, 0)], Gdk.DragAction.COPY | Gdk.DragAction.MOVE) #@UndefinedVariable
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
    
    def updates_tree_structure(self):
        self.hash.clear()
        for row in self.model:
            row[self.parent_level[0]] = None
            row[self.level[0]] = uuid.uuid4().hex
            self.hash[row[self.level[0]]] = row.iter         
            self.update_tree_structure_row_requrcive(row)
    
    def update_tree_structure_row_requrcive(self, row):        
        for child in row.iterchildren():
            child[self.parent_level[0]] = row[self.level[0]]
            child[self.level[0]] = uuid.uuid4().hex
            self.hash[child[self.level[0]]] = child.iter    
            self.update_tree_structure_row_requrcive(child)
   
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
    
    def add_reqursive_plain(self, from_model, from_iter, to_model, to_iter, parent_level):
        for child_row in self.get_child_rows(from_model, parent_level):            
            new_iter = to_model.get_model().append(to_iter, child_row)
            child_level = child_row[self.level[0]]
            self.add_reqursive_plain(from_model, from_iter, to_model, new_iter, child_level)
    
    def get_child_rows(self, model, parent_level):
        result = []
        for child_row in model:
            if child_row[self.parent_level[0]] == parent_level:
                result.append(child_row)        
        return result
    
    def on_drag_drop(self, to_tree, context, x, y, time):
        # ff - from_filter
        '''targets = {}
        for atom in context.list_targets():
            targets[atom] = atom'''
        to_tree.drag_get_data(context, context.list_targets()[-1], time)
        return True

    def rebuild_tree(self, tree):     
        if tree.current_view == VIEW_TREE:
            self.updates_tree_structure()
                
        if tree.current_view == VIEW_PLAIN:              
            self.update_tracknumber()
    
    def change_filepaths_in_row(self, model, iter, filepath):
        row = model[model.get_path(iter)]
        row[self.path[0]] = filepath
                
    def remove_replaced(self, model, rowrefs):
        for ref in rowrefs:
            iter = self.get_iter_from_row_reference(ref)
            iter = model.convert_iter_to_child_iter(iter)
            model.get_model().remove(iter)

    def add_m3u(self, from_model=None, from_iter=None, to_tree=None, to_model=None,
                to_iter=None, pos=None, row=None):
        if row:
            m3u_file_path = row[self.path[0]]
            m3u_title = row[self.text[0]]

        else:
            if from_model.get_model() is not to_model:
                m3u_file_path = from_model.get_value(from_iter, self.path[0])
                m3u_title = from_model.get_value(from_iter, self.text[0])
            else:
                return
            
        if m3u_file_path.startswith("http//"):
            return None
            
        paths = m3u_reader(m3u_file_path)
        paths.insert(0, [None, os.path.splitext(m3u_title)[0]])
            
        new_iter = None
        for i, path in enumerate(paths):
            if i == 0:
                bean = FModel(_("m3u playlist: ") + path[1]).add_is_file(False).add_font("bold")
            else:
                text = path[1]
                path = path[0]
                bean = FModel(path, path).add_is_file(True)
                if path.startswith("http"):
                    bean.add_type(FTYPE_RADIO)
                if text: bean.text = text
                        
            row = self.fill_beans_and_get_rows([bean])[0]                               
                       
            if new_iter:
                to_iter = new_iter
            new_iter = self.to_add_drag_item(to_tree, to_model, to_iter, pos, None,  row=row)
            
        return True
    
    def to_add_drag_item(self, to_tree=None, to_model=None, to_iter=None,  pos=None, ref=None, child=False, row=None):    
        if not row:
            from_iter = self.get_iter_from_row_reference(ref)
            from_model = ref.get_model()
            row = self.get_row_from_model_iter(from_model, from_iter)
            if not child and self.copy == Gdk.DragAction.MOVE:  # @UndefinedVariable
                self.row_to_remove.append(ref)
        
        if (to_tree and hasattr(to_tree, "current_view") 
                    and to_tree.current_view == VIEW_PLAIN):
            if pos == INTO_OR_BEFORE:
                pos = BEFORE
            elif pos == INTO_OR_AFTER:
                pos = AFTER
                
        if to_iter:
            if (to_model.get_value(to_iter, self.is_file[0]) and
                        pos in (INTO_OR_BEFORE, INTO_OR_AFTER)):
                pos = AFTER
            if pos in (INTO_OR_BEFORE, INTO_OR_AFTER):
                if child:
                    new_iter = to_model.append(to_iter, row)
                else:
                    new_iter = to_model.prepend(to_iter, row)
            elif pos == BEFORE:
                new_iter = to_model.insert_before(None, to_iter, row)
                
            elif pos == AFTER:
                new_iter = to_model.insert_after(None, to_iter, row)
            else:
                new_iter = to_model.append(None, row)
        else:
            new_iter = to_model.append(None, row)
        
        #to_tree.hash[row[self.level[0]]] = new_iter
        return new_iter

    def iter_is_parent(self, ff_row_ref, ff_model, to_tree, to_model, to_parent_iter, pos=INTO_OR_AFTER):
        ff_iter = self.get_iter_from_row_reference(ff_row_ref)
        #refs = self.content_filter(ff_iter, ff_model)
        refs = []
        for n in xrange(ff_model.iter_n_children(ff_iter)):
            ff_child_iter = ff_model.iter_nth_child(ff_iter, n)
            refs.append(self.get_row_reference_from_iter(ff_model, ff_child_iter)) 
        
        for ref in refs:
            iter = self.get_iter_from_row_reference(ref)
            to_child_iter = self.to_add_drag_item(to_tree, to_model, to_parent_iter, pos, ref, child=True)
            
            """Iters have already changed. Redefine"""
            iter = self.get_iter_from_row_reference(ref)
            
            if ff_model.iter_n_children(iter):
                to_child_iter = self.iter_is_parent(ref, ff_model, to_tree, to_model, to_child_iter)
            if to_tree.current_view == VIEW_PLAIN:
                to_parent_iter = to_child_iter
        return to_child_iter
                
    def content_filter(self, from_iter, from_model):
        cue_refs = []
        folder_refs = []
        not_cue_refs = []
        for n in xrange(from_model.iter_n_children(from_iter)):
            from_child_iter = from_model.iter_nth_child(from_iter, n)
            row_reference = self.get_row_reference_from_iter(from_model, from_child_iter)
                     
            ext = get_file_extension(from_model.get_value(from_child_iter, self.path[0]))
            if ext in [".m3u", ".m3u8"]: 
                logging.info("m3u is found. Skip it")
                continue
            elif ext == ".cue":
                logging.info("Cue is found. Skip other files")
                cue_refs.append(row_reference)
            else:
                if from_model.iter_has_child(from_child_iter):
                    folder_refs.append(row_reference)
                not_cue_refs.append(row_reference)
        
        return cue_refs + folder_refs if cue_refs else not_cue_refs
    

    
    def replace_inside_navig_tree(self, old_path, dest_folder):
        logging.debug('drag inside navigation tree')
        new_path = os.path.join(dest_folder, os.path.basename(old_path))
        if old_path != new_path:
            logging.debug('old file: ' + old_path)
            logging.debug('new file: ' + new_path)

            def task():
                if self.copy == Gdk.DragAction.MOVE: #@UndefinedVariable
                    copy_move_with_progressbar(self.pr_window, old_path, dest_folder, move=True)
                else:
                    copy_move_with_progressbar(self.pr_window, old_path, dest_folder)
                self.pr_window.response(Gtk.ResponseType.OK)
                            
            t = threading.Thread(target=task)
            t.start()
                        
            if self.pr_window.run() == Gtk.ResponseType.REJECT:
                self.pr_window.exit = True
                t.join()
           
            return new_path
        else:
            logging.debug("Destination folder same as file folder. Skipping")
            return None
    
    def get_dest_folder(self, to_f_model, to_filter_iter, to_filter_path):
        if to_filter_iter:
            path = to_f_model.get_value(to_filter_iter, self.path[0])
            if os.path.isdir(path):
                return path            
            parent_iter = to_f_model.iter_parent(to_filter_iter)
        else:
            return FCache().music_paths[self.controls.tabhelper.get_current_page()][-1]
        if not parent_iter:
            logging.debug("no parent iter found")
            if to_filter_path[-1] > 0:
                previous_iter = to_f_model.get_iter((to_filter_path[-1] - 1,))
                previous_path = to_f_model.get_value(previous_iter, self.path[0])
                dest_folder = os.path.dirname(previous_path) 
            else:
                logging.debug("item is top in tree")
                next_path = to_f_model.get_value(to_f_model.get_iter_first(), self.path[0])
                dest_folder = os.path.dirname(next_path)
        else:
            dest_folder = to_f_model.get_value(parent_iter, self.path[0])
            
        return dest_folder
        
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
            if self.filling_lock.locked():
                self.filling_lock.release()
    
    def tree_append_all(self, beans):
        def task():
            self._tree_append_all(beans)
        GObject.idle_add(task)
        
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
    
    def get_all_beans_by_parent(self, model, iter):
        bean = [self.get_bean_from_model_iter(model, iter)]
        if bean and bean[0].path and bean[0].path.lower().endswith(".iso.wv"):
            bean = get_beans_from_iso_wv(bean[0].path)
        beans = bean + self.get_child_beans_by_parent(model, iter)
        return beans
        
    def plain_append_all(self, beans, parent=None):
        def task():
            try:
                self._plain_append_all(beans, parent)
            finally:
                if "PlaylistTreeControl" in str(self):
                    thread.start_new_thread(self.controls.notetabs.on_save_tabs, ())
        GObject.idle_add(task)
    
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
              
        counter = 0
        for bean in beans:
            if not bean.path or not get_file_extension(bean.path) == ".cue":                                        
                if bean.is_file and FC().numbering_by_order:
                    counter += 1
                    bean.tracknumber = counter
                else: 
                    counter = 0
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
            
    def fill_beans_and_get_rows(self, beans, filter=None):
        if filter:
            beans = filter(beans)
        full_beans = update_id3_wind_filtering(beans)
        rows = []
        for one in full_beans:
            one.visible = True
            one.update_uuid() 
            row = self.get_row_from_bean(one)
            rows.append(row)
        return rows
    
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
            GObject.idle_add(self.update_tracknumber, priority=GObject.PRIORITY_LOW + 1)
    
    @idle_task_priority(GObject.PRIORITY_LOW)
    def insert_bean(self, row_ref, bean):
        if row_ref.valid():
            row = self.get_row_from_bean(bean)
            iter = self.model.insert_after(None, self.get_iter_from_row_reference(row_ref), row)
            self.fill_row(self.get_row_reference_from_iter(self.model, iter), bean)

    @idle_task_priority(GObject.PRIORITY_LOW)
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


    def playlist_filter(self, rows):
        checked_cue_rows = []
        checked_m3u_rows = []
        m3u_rows_for_delete = []

        def task(rows):
            for row in rows:
                index = self.path[0]
                path = row[index]
                if path and (get_file_extension(path) in [".m3u", ".m3u8"]
                             and row not in checked_m3u_rows):
                    checked_m3u_rows.append(row)
                    for r in rows:
                        if (os.path.dirname(r[index]) == os.path.dirname(path) and os.path.isfile(r[index])
                            and get_file_extension(r[index]) not in [".m3u", ".m3u8"]):
                                m3u_rows_for_delete.append(row)
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