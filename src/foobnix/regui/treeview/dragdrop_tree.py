'''
Created on Oct 14, 2010

@author: ivan
'''

import gtk
import sys
import copy
import time
import uuid
import gobject
import logging
import os.path
import threading

from foobnix.cue.cue_reader import CueReader
from foobnix.fc.fc import FC
from foobnix.fc.fc_cache import FCache
from foobnix.helpers.dialog_entry import info_dialog
from foobnix.helpers.window import CopyProgressWindow
from foobnix.util.const import BEFORE, AFTER, INTO_OR_BEFORE, INTO_OR_AFTER
from foobnix.util.file_utils import copy_move_files_dialog, copy_move_with_progressbar,\
    get_file_extension
from foobnix.util.m3u_utils import m3u_reader
from foobnix.util.id3_file import update_id3_wind_filtering
from foobnix.util.iso_util import get_beans_from_iso_wv
from foobnix.regui.model import FModel, FTreeModel


VIEW_PLAIN = 0
VIEW_TREE = 1

class DragDropTree(gtk.TreeView):
    def __init__(self, controls):
        self.controls = controls
        gtk.TreeView.__init__(self)
        
        self.connect("drag-begin", self.on_drag_begin)
        self.connect("drag-drop", self.on_drag_drop)
        self.copy = False
        
        """init values"""
        self.hash = {None:None}
        self.current_view = None
    
    def on_drag_begin(self, widget, drag_context):
        ff_model, ff_paths = widget.get_selection().get_selected_rows() #@UnusedVariable
        if len(ff_paths) > 1:
            self.drag_source_set_icon_stock('gtk-dnd-multiple')
        else:
            self.drag_source_set_icon_stock('gtk-dnd')
                
    def configure_recive_drag(self):
        self.enable_model_drag_dest([("text/uri-list", 0, 0)], gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE) #@UndefinedVariable
    
    def configure_send_drag(self):
        #self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("text/uri-list", 0, 0)], gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE) #@UndefinedVariable
        self.drag_source_set(gtk.gdk.BUTTON1_MASK, [("text/uri-list", 0, 0)],gtk.gdk.ACTION_COPY|gtk.gdk.ACTION_MOVE) #@UndefinedVariable
    
    def append_all(self, beans):
        logging.debug("begin append all")
        if self.current_view == VIEW_PLAIN:
            self.plain_append_all(beans)            
        else:
            self.tree_append_all(beans)
    
    def simple_append_all(self, beans):
        logging.debug("simple_append_all")
        logging.debug(self.current_view)
        
        if self.current_view == VIEW_PLAIN:
            logging.debug("simple_append_all")
            for bean in beans:
                row = self.get_row_from_bean(bean)            
                self.model.append(None, row)               
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
        for row in self.model:
            row[self.parent_level[0]] = None
            row[self.level[0]] = uuid.uuid4().hex             
            self.update_tree_structure_row_requrcive(row)
    
    def update_tree_structure_row_requrcive(self, row):        
        for child in row.iterchildren():
            child[self.parent_level[0]] = row[self.level[0]]
            child[self.level[0]] = uuid.uuid4().hex   
            self.update_tree_structure_row_requrcive(child)
   
    def get_bean_from_model_iter(self, model, iter):
        if not model or not iter:
            return None
        bean = FModel()
        id_dict = FTreeModel().cut().__dict__
        for key in id_dict.keys():
            num = id_dict[key]
            val = model.get_value(iter, num)
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
    
    def on_drag_drop(self, to_tree, drag_context, x, y, selection):
        # ff - from_filter
        self.copy = drag_context.action
        to_filter_model = to_tree.get_model()
        to_model = to_filter_model.get_model()
        if to_tree.get_dest_row_at_pos(x, y):
            to_filter_path, to_filter_pos = to_tree.get_dest_row_at_pos(x, y)
            to_filter_iter = to_filter_model.get_iter(to_filter_path)
            to_iter = to_filter_model.convert_iter_to_child_iter(to_filter_iter)
        else:
            to_filter_path = None
            to_filter_pos = None     
            to_filter_iter = None
            to_iter = None
            
        from_tree = drag_context.get_source_widget()        
        
        if not from_tree: return None
        
        ff_model, ff_paths = from_tree.get_selection().get_selected_rows()
        
        if "PlaylistTreeControl" in str(to_tree) and to_tree != from_tree:
            self.controls.search_progress.start()
            self.spinner = True
            def task(to_iter):
                all_rows = []
                for ff_path in ff_paths:
                    ff_iter = ff_model.get_iter(ff_path)
                    beans = self.get_all_beans_by_parent(ff_model, ff_iter)
                    all_rows += self.fill_beans_and_get_rows(beans, self.simple_content_filter)
                
                self.spinner = False
                    
                for i, row in enumerate(all_rows):
                        pos = AFTER if i else to_filter_pos
                        if row[self.path[0]] and get_file_extension(row[self.path[0]]) in [".m3u", ".m3u8"]:
                            self.add_m3u(ff_model, ff_iter, to_tree, to_model, to_iter, pos)
                            continue
                        to_iter = self.to_add_drag_item(to_tree, to_model, to_iter, pos, None, row=row)
                self.controls.search_progress.stop()
                self.update_tracknumber()
                                          
            t = threading.Thread(target=task, args=(to_iter,))
            t.start()
            """trick to show spinner before end of handling"""
            while t.isAlive():
                time.sleep(0.1)
                while gtk.events_pending():
                    if self.spinner:#self.controls.search_progress.get_property('active'):
                        gtk.main_iteration()
                    else:
                        break # otherwise endless cycle'''
                    
            return 
        
        new_iter = None
        self.row_to_remove = []
        
        ff_row_refs = [gtk.TreeRowReference(ff_model, ff_path) for ff_path in ff_paths]
        
        """to tree is NavigationTreeControl"""
        is_copy_move = False
        if isinstance(self, self.controls.tree.__class__):
            if from_tree is not to_tree:
                return
            if sys.version_info < (2, 6):
                return
            dest_folder = self.get_dest_folder(to_filter_model, to_filter_iter, to_filter_path)
            rows = [to_model[ff_path] for ff_path in ff_paths]
            files = [row[self.path[0]] for row in rows if os.path.dirname(row[self.path[0]]) != dest_folder]
            if to_filter_pos:
                if os.path.isfile(to_filter_model[to_filter_path][self.path[0]]):
                    if to_filter_pos != BEFORE:
                        to_filter_pos = AFTER
                elif to_filter_pos in (BEFORE, 
                                       AFTER):
                    info_dialog(_("Attention!!!"), 
                                _("When you release the mouse button the mouse" +
                                 " pointer must be over the folder exactly." +
                                 " Please retry!"))
                    return
            if files and copy_move_files_dialog(files, dest_folder, self.copy):
                is_copy_move = True
                text = _("Copying:") if self.copy == gtk.gdk.ACTION_COPY else _("Replacing:") #@UndefinedVariable
                self.pr_window = CopyProgressWindow(_("Progress"), files, 300, 100)
                self.pr_window.label_from.set_text(text)
                self.pr_window.label_to.set_text(_("To: ") + dest_folder + "\n")
                for ff_path, ff_row_ref, file in zip(ff_paths, ff_row_refs, files):
                    new_path = self.replace_inside_navig_tree(file, dest_folder)
                    if not new_path: continue
                    self.one_row_replacing(ff_row_ref, ff_path, ff_model, from_tree,
                        to_tree, to_model, to_iter, to_filter_pos, to_filter_path,
                        new_iter, new_path, is_copy_move)
                self.remove_replaced(ff_model)
                self.pr_window.destroy()
                self.save_beans_from_tree()
            return
                      
        for ff_row_ref in ff_row_refs: 
            new_iter = self.one_row_replacing(ff_row_ref, ff_path, ff_model, from_tree,
                                  to_tree, to_model, to_iter, to_filter_pos, to_filter_path,
                                  new_iter)
        
        if from_tree == to_tree:
            self.remove_replaced(ff_model)
            
        self.row_to_remove = []
   
        self.rebuild_tree(to_tree)        
        
    def one_row_replacing(self, ff_row_ref, ff_path, ff_model, from_tree,
                           to_tree, to_model, to_iter, to_filter_pos, to_filter_path, 
                           new_iter, new_path=None, is_copy_move=False):
        
        ff_iter = self.get_iter_from_row_reference(ff_row_ref)
                    
        """do not copy to himself"""
        if to_tree == from_tree and ff_path == to_filter_path:
            #drag_context.finish(False, False)
            return None
           
        """if m3u is dropped"""
        if self.add_m3u(ff_model, ff_iter, to_tree, to_model, to_iter, to_filter_pos):
            return
            
        if ff_model.iter_has_child(ff_iter):
            new_iter = self.to_add_drag_item(to_tree, to_model, to_iter, to_filter_pos, ff_row_ref)
            self.iter_is_parent(ff_row_ref, ff_model, to_tree, to_model, new_iter)
            if is_copy_move:
                self.change_filepaths_in_row(to_model, new_iter, new_path)
        else:
            if new_iter and to_iter:
                to_iter = new_iter
            new_iter = self.to_add_drag_item(to_tree, to_model, to_iter, to_filter_pos, ff_row_ref)
            if is_copy_move:
                self.change_filepaths_in_row(to_model, new_iter, new_path)
            if to_filter_pos == BEFORE:
                new_iter = to_model.iter_next(new_iter)
            elif to_filter_pos == INTO_OR_BEFORE:
                new_iter = to_iter
                
        '''drag row with children from plain tree'''    
        if from_tree.current_view == VIEW_PLAIN:
            ff_iter = self.get_iter_from_row_reference(ff_row_ref)
            if not self.get_bean_from_model_iter(ff_model, ff_iter).is_file:
                next_iter = ff_model.iter_next(ff_iter)
                _iter = new_iter
                while self.get_bean_from_model_iter(ff_model, next_iter).is_file:
                    ref = self.get_row_reference_from_iter(ff_model, next_iter)
                    if to_tree.current_view == VIEW_TREE:
                        if _iter == new_iter:
                            pos = INTO_OR_AFTER
                            if to_filter_pos == BEFORE:
                                _iter = self.get_previous_iter(to_model, _iter)
                        else:
                            pos = AFTER
                    else:
                        pos = to_filter_pos
                    _iter = self.to_add_drag_item(to_tree, to_model, _iter, pos, ref)
                    next_iter = self.get_iter_from_row_reference(ref)
                    next_iter = ff_model.iter_next(next_iter)
                    if not next_iter: break
        
        return new_iter  
            
        
    def rebuild_tree(self, tree):     
        if tree.current_view == VIEW_TREE:
            self.updates_tree_structure()
                
        if tree.current_view == VIEW_PLAIN:              
            #self.rebuild_as_plain()
            self.update_tracknumber()
    
    def change_filepaths_in_row(self, model, iter, filepath):
        row = model[model.get_path(iter)]
        row[self.path[0]] = filepath
                
    def remove_replaced(self, ff_model):
        for ref in self.row_to_remove:
            filter_iter = self.get_iter_from_row_reference(ref)
            iter = ff_model.convert_iter_to_child_iter(filter_iter)
            ff_model.get_model().remove(iter)
    
    def add_m3u(self, from_model=None, from_iter=None, to_tree=None, to_model=None,
                to_iter=None, pos=None, row=None):
        if row:
            if get_file_extension(row[self.path[0]]) in [".m3u", ".m3u8"]:
                m3u_file_path = row[self.path[0]]
                m3u_title = row[self.text[0]]
            else:
                return
        else:
            if ((from_model.get_value(from_iter, 0).lower().endswith(".m3u") 
            or from_model.get_value(from_iter, 0).lower().endswith(".m3u8"))
            and from_model.get_model() is not to_model):
                    m3u_file_path = from_model.get_value(from_iter, self.path[0])
                    m3u_title = from_model.get_value(from_iter, self.text[0])
            else:
                return
            
            if m3u_file_path.startswith("http//"):
                return None
            
        paths = m3u_reader(m3u_file_path)
        paths.insert(0, os.path.splitext(m3u_title)[0])
        first_path = paths[0][0] if isinstance(paths[0], list) else paths[0]
        if first_path:
            list_path = first_path[0].split("/")
            name = list_path[len(list_path) - 2]
            parent = FModel(name)
            
        new_iter = None
        for i, path in enumerate(paths):
            if isinstance(path, list):
                text = path[1]
                path = path[0]
                bean = FModel(path, path).add_is_file(True)
                if text: bean.text = text
                
                        
            elif not i:
                bean = FModel(_("m3u playlist: ") + path).add_is_file(False).add_font("bold")
            else:
                bean = FModel(path, path).parent(parent)
            
            row = self.fill_beans_and_get_rows([bean])[0]                               
                        
            if new_iter:
                to_iter = new_iter
            new_iter = self.to_add_drag_item(to_tree, to_model, to_iter, pos, None,  row=row)
            
        return True
    
    def to_add_drag_item(self, to_tree, to_model, to_iter,  pos, ref=None, child=False, row=None):    
        if (to_tree and hasattr(to_tree, "current_view") 
                    and to_tree.current_view == VIEW_PLAIN):
            if pos == INTO_OR_BEFORE:
                pos = BEFORE
            elif pos == INTO_OR_AFTER:
                pos = AFTER
        
        if not row:
            from_iter = self.get_iter_from_row_reference(ref)
            from_model = ref.get_model()
            row = self.get_row_from_model_iter(from_model, from_iter)
            if not child and self.copy == gtk.gdk.ACTION_MOVE: #@UndefinedVariable
                self.row_to_remove.append(ref)
        
        if to_iter:
            if (self.model.get_value(to_iter, FTreeModel().is_file[0]) and
                pos in (INTO_OR_BEFORE,INTO_OR_AFTER)):
                pos = AFTER
            if pos in (INTO_OR_BEFORE,INTO_OR_AFTER):
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
     
        return new_iter

    def iter_is_parent(self, ff_row_ref, ff_model, to_tree, to_model, to_parent_iter, pos=INTO_OR_AFTER):
        ff_iter = self.get_iter_from_row_reference(ff_row_ref)
        refs = self.content_filter(ff_iter, ff_model) 
        for ref in refs:
            iter = self.get_iter_from_row_reference(ref)
            file_name = ff_model.get_value(iter, self.path[0])
            ext = get_file_extension(file_name)
            if ext == ".cue" and to_tree.current_view == VIEW_PLAIN:
                last_iter = to_parent_iter
                cue_beans = CueReader(file_name).get_common_beans()
                for bean in cue_beans:
                    row = self.get_row_from_bean(bean)
                    to_child_iter = self.to_add_drag_item(to_tree, to_model, last_iter, None, None, child=True, row=row)
                    last_iter = to_child_iter
            else:
                to_child_iter = self.to_add_drag_item(to_tree, to_model, to_parent_iter, pos, ref, child=True)
            
            """Iters have already changed. Redefine"""
            iter = self.get_iter_from_row_reference(ref)
            
            if  ff_model.iter_n_children(iter):
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
    
    def simple_content_filter(self, beans):
        checked_cue_beans = []
        checked_m3u_beans = []
        m3u_beans_for_delete = []
        def task(beans):
            for bean in beans:
                path = bean.path
                if path and (get_file_extension(path) in [".m3u", ".m3u8"]
                    and bean not in checked_m3u_beans):
                    checked_m3u_beans.append(bean)
                    for b in beans:
                        if (os.path.dirname(b.path) == os.path.dirname(path) and os.path.isfile(b.path)
                            and get_file_extension(b.path) not in [".m3u", ".m3u8"]):
                                m3u_beans_for_delete.append(bean)
                                break
                    task(beans)
                    
                if path and (get_file_extension(path) == ".cue" 
                    and bean not in checked_cue_beans):
                    
                    checked_cue_beans.append(bean)
                    filtered_beans = [b for b in beans if (os.path.dirname(b.path) != os.path.dirname(path)
                                                           or os.path.isdir(b.path) 
                                                           or get_file_extension(b.path) == ".cue")]
                    return task(filtered_beans)
            return beans
        
        all_filtered_beans = task(beans)
        return [bean for bean in all_filtered_beans 
                if bean not in m3u_beans_for_delete] if m3u_beans_for_delete else all_filtered_beans
    
    def replace_inside_navig_tree(self, old_path, dest_folder):
        logging.debug('drag inside navigation tree')
        new_path = os.path.join(dest_folder, os.path.basename(old_path))
        if old_path != new_path:
            logging.debug('old file: ' + old_path)
            logging.debug('new file: ' + new_path)
            def task():
                if self.copy == gtk.gdk.ACTION_MOVE: #@UndefinedVariable
                    copy_move_with_progressbar(self.pr_window, old_path, dest_folder, move=True)
                else:
                    copy_move_with_progressbar(self.pr_window, old_path, dest_folder)
                self.pr_window.response(gtk.RESPONSE_OK)
                            
            t = threading.Thread(target=task)
            t.start()
                        
            if self.pr_window.run() == gtk.RESPONSE_REJECT:
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
                previous_iter = to_f_model.get_iter( (to_filter_path[-1] -1,) )
                previous_path = to_f_model.get_value(previous_iter , self.path[0])
                dest_folder = os.path.dirname(previous_path) 
            else:
                logging.debug("item is top in tree")
                next_path = to_f_model.get_value(to_f_model.get_iter_root(), self.path[0])
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
        self.current_view = VIEW_PLAIN
        tn = self.tracknumber[0]
        path = self.path[0]
        isfile = self.is_file[0]
        counter = 0
        for row in self.model:
            if not row[path] or not get_file_extension(row[path]) == ".cue":
                if row[isfile] and FC().numbering_by_order:
                    counter += 1
                else:
                    counter = 0
                if counter:
                    row[tn] = counter
    
    def tree_append_all(self, beans):
        def task():
            self._tree_append_all(beans)
        gobject.idle_add(task)
        
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
            self._plain_append_all(beans, parent)
        gobject.idle_add(task)
    
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
        if bean.is_file == True:
            bean.font = "normal"
        else:
            bean.font = "bold"
            
        bean.visible = True
        beans = update_id3_wind_filtering([bean])
        for one in beans:
            one.update_uuid() 
            row = self.get_row_from_bean(one)            
            """append to tree thread safe"""
            
            
            """append to tree thread safe end"""
            logging.debug(row)
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
        if bean.is_file == True:
            bean.font = "normal"
        else:
            bean.font = "bold"
        
        """copy beans"""
        bean = copy.copy(bean)
        bean.visible = True

        if self.hash.has_key(bean.get_parent()):
            parent_iter_exists = self.hash[bean.get_parent()]
        else:
            parent_iter_exists = None
        row = self.get_row_from_bean(bean)
        
        parent_iter = self.model.append(parent_iter_exists, row)
        self.hash[bean.level] = parent_iter
