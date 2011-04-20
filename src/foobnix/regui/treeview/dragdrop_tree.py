'''
Created on Oct 14, 2010

@author: ivan
'''

import gtk
import sys
import copy
import uuid
import gobject
import logging
import os.path
import threading

from foobnix.fc.fc import FC
from foobnix.fc.fc_cache import FCache
from foobnix.util.m3u_utils import m3u_reader
from foobnix.regui.model import FModel, FTreeModel
from foobnix.util.iso_util import get_beans_from_iso_wv
from foobnix.util.id3_file import update_id3_wind_filtering
from foobnix.util.file_utils import copy_move_files_dialog, copy_move_with_progressbar
from foobnix.helpers.window import CopyProgressWindow


VIEW_PLAIN = 0
VIEW_TREE = 1

class DragDropTree(gtk.TreeView):
    def __init__(self, controls):
        self.controls = controls
        gtk.TreeView.__init__(self)
        
        self.connect("drag-drop", self.on_drag_drop)
        self.copy = False
        
        """init values"""
        self.hash = {None:None}
        self.current_view = None
                
    def configure_recive_drag(self):
        self.enable_model_drag_dest([("example1", 0, 0)], gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE) #@UndefinedVariable
    
    def configure_send_drag(self):
        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example1", 0, 0)], gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE) #@UndefinedVariable
    
    
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
                
        new_iter = None
        self.row_to_remove = []
        
        ff_row_refs = [gtk.TreeRowReference(ff_model, ff_path) for ff_path in ff_paths]
        
        """to tree is NavigationTreeControl"""
        is_copy_move = False
        if isinstance(self, self.controls.tree.__class__) and from_tree is to_tree:
            if sys.version_info < (2, 6):
                return
            dest_folder = self.get_dest_folder(to_filter_model, to_filter_iter, to_filter_path)
            rows = [to_model[ff_path] for ff_path in ff_paths]
            files = [row[self.path[0]] for row in rows if os.path.dirname(row[self.path[0]]) != dest_folder]
            if (to_filter_pos and ((to_filter_pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE)
                or (to_filter_pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER))
            	and os.path.isfile(to_filter_model[to_filter_path][self.path[0]])):
                    to_filter_pos = gtk.TREE_VIEW_DROP_AFTER
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
                        to_model, to_tree, to_iter, to_filter_pos, to_filter_path,
                        new_iter, new_path, is_copy_move)
                self.remove_replaced(ff_model)
                self.pr_window.destroy()
                self.save_beans_from_tree()
            return
               
        for ff_row_ref in ff_row_refs:        
            self.one_row_replacing(ff_row_ref, ff_path, ff_model, from_tree,
                                  to_model, to_tree, to_iter, to_filter_pos, to_filter_path,
                                  new_iter)
    
        if from_tree == to_tree:
            self.remove_replaced(ff_model)
            
        self.row_to_remove = []
   
        self.rebuild_tree(to_tree)        
        
    def one_row_replacing(self, ff_row_ref, ff_path, ff_model, from_tree,
                           to_model, to_tree, to_iter, to_filter_pos, to_filter_path, 
                           new_iter, new_path=None, is_copy_move=False):
        
        ff_iter = self.get_iter_from_row_reference(ff_row_ref)
                    
        """do not copy to himself"""
        if to_tree == from_tree and ff_path == to_filter_path:
            #drag_context.finish(False, False)
            return None
           
        """if m3u is dropped"""
        if self.add_m3u(ff_model, ff_iter, to_model, to_iter, to_filter_pos):
            return
            
        if ff_model.iter_has_child(ff_iter):
            new_iter = self.to_add_drag_item(to_model, to_iter, to_filter_pos, ff_row_ref)
            self.iter_is_parent(ff_row_ref, ff_model, to_model, new_iter)
            if is_copy_move:
                self.change_filepaths_in_row(to_model, new_iter, new_path)
        else:
            if new_iter and to_iter and not to_model.iter_has_child(to_iter):
                to_iter = new_iter
            new_iter = self.to_add_drag_item(to_model, to_iter, to_filter_pos, ff_row_ref)
            if is_copy_move:
                self.change_filepaths_in_row(to_model, new_iter, new_path)
            if to_filter_pos == gtk.TREE_VIEW_DROP_BEFORE:
                new_iter = to_model.iter_next(new_iter)
                      
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
                            pos = gtk.TREE_VIEW_DROP_INTO_OR_AFTER
                            if to_filter_pos == gtk.TREE_VIEW_DROP_BEFORE:
                                _iter = self.get_previous_iter(to_model, _iter)
                        else:
                            pos = gtk.TREE_VIEW_DROP_AFTER
                    else:
                        pos = to_filter_pos
                    _iter = self.to_add_drag_item(to_model, _iter, pos, ref)
                    next_iter = self.get_iter_from_row_reference(ref)
                    next_iter = ff_model.iter_next(next_iter)
                    if not next_iter: break
          
            
        
    def rebuild_tree(self, tree):     
        if tree.current_view == VIEW_TREE:
            self.updates_tree_structure()
                
        if tree.current_view == VIEW_PLAIN:              
            self.rebuild_as_plain()
    
    def change_filepaths_in_row(self, model, iter, filepath):
        row = model[model.get_path(iter)]
        row[self.path[0]] = filepath
                
    def remove_replaced(self, ff_model):
        for ref in self.row_to_remove:
            filter_iter = self.get_iter_from_row_reference(ref)
            iter = ff_model.convert_iter_to_child_iter(filter_iter)
            ff_model.get_model().remove(iter)
    
    def add_m3u(self, from_model, from_iter, to_model, to_iter, pos):
        if ((from_model.get_value(from_iter, 0).lower().endswith(".m3u") 
        or from_model.get_value(from_iter, 0).lower().endswith(".m3u8"))
        and from_model.get_model() is not to_model):
            m3u_file_path = from_model.get_value(from_iter, 5)
            m3u_title = from_model.get_value(from_iter, 0)
            paths = m3u_reader(m3u_file_path)
            paths.insert(0, os.path.splitext(m3u_title)[0])
            list = paths[0].split("/")
            name = list[len(list) - 2]
            parent = FModel(name)
            new_iter = None
            for i, path in enumerate(paths):
                if not i:
                    bean = FModel(path)
                else:
                    bean = FModel(path, path).parent(parent)
                
                row = self.get_row_from_bean(bean)
                
                if new_iter:
                    to_iter = new_iter
                new_iter = self.to_add_drag_item(to_model, to_iter, pos, None,  row=row)
                
            return True
    
    def to_add_drag_item(self, to_model, to_iter,  pos, ref=None, child=False, row=None):    
        if not row:
            from_iter = self.get_iter_from_row_reference(ref)
            from_model = ref.get_model()
            row = self.get_row_from_model_iter(from_model, from_iter)
            if not child and self.copy == gtk.gdk.ACTION_MOVE: #@UndefinedVariable
                self.row_to_remove.append(ref)
        if to_iter:
            if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
                if child:
                    new_iter = to_model.append(to_iter, row)
                else:
                    new_iter = to_model.prepend(to_iter, row)
            elif pos == gtk.TREE_VIEW_DROP_BEFORE:
                new_iter = to_model.insert_before(None, to_iter, row)
                
            elif pos == gtk.TREE_VIEW_DROP_AFTER:
                new_iter = to_model.insert_after(None, to_iter, row)
            else:
                new_iter = to_model.append(None, row)
        else:
            new_iter = to_model.append(None, row)
     
        return new_iter

    def iter_is_parent(self, ff_row_ref, ff_model, to_model, to_parent_iter, pos=gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
        ff_iter = self.get_iter_from_row_reference(ff_row_ref)
        refs = self.content_filter(ff_iter, ff_model) 
        for ref in refs:
            to_child_iter = self.to_add_drag_item(to_model, to_parent_iter, pos, ref, child=True)
            """Iters have already changed. Redefine"""
            iter = self.get_iter_from_row_reference(ref)
            if  ff_model.iter_n_children(iter):
                self.iter_is_parent(ref, ff_model, to_model, to_child_iter)
    
    def content_filter(self, from_iter, from_model):
        cue_refs = []
        folder_refs = []
        not_cue_refs = []
        for n in xrange(from_model.iter_n_children(from_iter)):
            from_child_iter = from_model.iter_nth_child(from_iter, n)
            row_reference = self.get_row_reference_from_iter(from_model, from_child_iter)
            if (from_model.get_value(from_child_iter, 0).endswith(".m3u") 
                or from_model.get_value(from_child_iter, 0).endswith(".m3u8")):
                logging.info("m3u is found. Skip it")
                continue
            elif from_model.get_value(from_child_iter, 0).endswith(".cue"):
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
            
        #attention! clear_tree() has low priority
        self.clear_tree()
        
        self.plain_append_all(copy_beans)
    
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
        if model.iter_has_child(iter):
            for i in xrange(model.iter_n_children(iter)):
                next_iter = model.iter_nth_child(iter, i)
                
                parent = self.get_bean_from_model_iter(model, next_iter)                
                list.append(parent)
                 
                beans = self.get_child_beans_by_parent(model, next_iter)
                
                for bean in beans:
                    bean.parent(parent)                
                    list.append(bean)
                
        return list
    
    
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
            if bean.path and not bean.path.lower().endswith(".cue"):                                        
                if bean.is_file and FC().numbering_by_order:
                    counter += 1
                    bean.tracknumber = counter
                else: 
                    counter = 0
            self._plain_append(bean, parent_iter)
            
    def _plain_append(self, bean, parent_iter):
        logging.debug("Plain append task" + str(bean.text) + str(bean.path))
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