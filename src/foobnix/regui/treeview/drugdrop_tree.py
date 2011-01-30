'''
Created on Oct 14, 2010

@author: ivan
'''
import gtk
import copy
import uuid
import os.path
import logging

from foobnix.regui.model import FModel, FTreeModel
from foobnix.util.id3_util import update_id3_wind_filtering
from foobnix.util.iso_util import get_beans_from_iso_wv
from foobnix.util.m3u_utils import m3u_reader
from foobnix.util.key_utils import is_key_control

VIEW_PLAIN = 0
VIEW_TREE = 1

class DrugDropTree(gtk.TreeView):
    def __init__(self, controls):
        self.controls = controls
        gtk.TreeView.__init__(self)
        
        self.connect("drag-drop", self.on_drag_drop)
        self.connect("key-press-event", self.on_key_event)
        self.connect("key-release-event", self.on_key_event)
        self.to_copy = False
        """init values"""
        self.hash = {None:None}
        self.current_view = None
    
    def configure_recive_drug(self):
        self.enable_model_drag_dest([("example1", 0, 0)], gtk.gdk.ACTION_COPY) #@UndefinedVariable
    
    def configure_send_drug(self):
        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK, [("example1", 0, 0)], gtk.gdk.ACTION_COPY) #@UndefinedVariable
    
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
        
        ff_row_refs = [gtk.TreeRowReference(ff_model, ff_path) for ff_path in ff_paths]
                
        new_iter = None
        self.row_to_remove = []        
        for ff_row_ref  in ff_row_refs:
            ff_iter = self.get_iter_from_row_reference(ff_row_ref)
                        
            """do not copy to himself"""
            if to_tree == from_tree and ff_path == to_filter_path:
                drag_context.finish(False, False)
                return None
            
            """if m3u is dropped"""
            if self.add_m3u(ff_model, ff_iter, to_model, to_iter, to_filter_pos):
                continue
            
            if ff_model.iter_has_child(ff_iter):
                new_iter = self.to_add_drug_item(to_model, to_iter, ff_row_ref, to_filter_pos, True)
                self.iter_is_parent(ff_row_ref, ff_model, to_model, new_iter)
            else:
                if new_iter:
                    to_iter = new_iter
                new_iter = self.to_add_drug_item(to_model, to_iter, ff_row_ref, to_filter_pos)
                
            if from_tree.current_view == VIEW_PLAIN:
                ff_iter = self.get_iter_from_row_reference(ff_row_ref)
                if not self.get_bean_from_model_iter(ff_model, ff_iter).is_file:
                    next_iter = ff_model.iter_next(ff_iter)
                    iter = new_iter
                    
                    while self.get_bean_from_model_iter(ff_model, next_iter).is_file:
                        ref = self.get_row_reference_from_iter(ff_model, next_iter)
                        if to_tree.current_view == VIEW_TREE:
                            if iter == new_iter:
                                pos = gtk.TREE_VIEW_DROP_INTO_OR_AFTER
                                if to_filter_pos == gtk.TREE_VIEW_DROP_BEFORE:
                                    iter = self.get_previous_iter(to_model, iter)
                            else:
                                pos = gtk.TREE_VIEW_DROP_AFTER
                        else:
                            pos = to_filter_pos
                        
                        iter = self.to_add_drug_item(to_model, iter, ref, pos)
                        next_iter = self.get_iter_from_row_reference(ref)
                        next_iter = ff_model.iter_next(next_iter)
                        if not next_iter: break
                
        def remove_replaced():
            for ref in self.row_to_remove:
                filter_iter = self.get_iter_from_row_reference(ref)
                iter = ff_model.convert_iter_to_child_iter(filter_iter)
                ff_model.get_model().remove(iter)    
        
        if from_tree == to_tree:
            remove_replaced()
        self.row_to_remove = []
        
        if to_tree.current_view == VIEW_TREE:
            self.updates_tree_structure()
                
        if to_tree.current_view == VIEW_PLAIN:              
            self.rebuild_as_plain()
                
 
    def add_m3u(self, from_model, from_iter, to_model, to_iter, pos):
        if (from_model.get_value(from_iter, 0).lower().endswith(".m3u") 
        or from_model.get_value(from_iter, 0).lower().endswith(".m3u8")):
            logging.info("m3u is found")
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
                new_iter = self.to_add_drug_item(to_model, to_iter, None,  pos, row=row)
                
            return True
    
    def to_add_drug_item(self, to_model, to_iter, ref, pos, parent=False, child=False, row=None):    
        if not row:
            from_iter = self.get_iter_from_row_reference(ref)
            from_model = ref.get_model()
            row = self.get_row_from_model_iter(from_model, from_iter)
            if not child and not self.to_copy:
                self.row_to_remove.append(ref)
        if to_iter:
            if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
                if child:
                    new_iter = to_model.append(to_iter, row)
                else:
                    new_iter = to_model.prepend(to_iter, row)
            elif pos == gtk.TREE_VIEW_DROP_BEFORE:
                new_iter = to_model.insert_before(None, to_iter, row)
                if not parent:
                    new_iter = to_model.iter_next(new_iter)
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
            to_child_iter = self.to_add_drug_item(to_model, to_parent_iter, ref, pos, child=True)
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
        if not beans:
            return None
        self.current_view = VIEW_TREE
        logging.debug("append all as tree")
       
        for bean in beans:    
            self.tree_append(bean)
    
    def plain_append_all(self, beans):
        logging.debug("begin plain append all")
        if not beans:
            return
        self.current_view = VIEW_PLAIN
        
        normalized = []
        for model in beans:
            if model.path and model.path.lower().endswith(".iso.wv"):
                logging.debug("begin normalize iso.wv" + str(model.path))
                all = get_beans_from_iso_wv(model.path)
                for inner in all:
                    normalized.append(inner)
            else:
                normalized.append(model)
        beans = normalized
              
        counter = 0
        for bean in beans:
            if bean.path and not bean.path.lower().endswith(".cue"):                                        
                if bean.is_file:
                    counter += 1
                    bean.tracknumber = counter
                else: 
                    counter = 0
            self._plain_append(bean)
            
    def _plain_append(self, bean):
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
            
            self.model.append(None, row)            
            """append to tree thread safe end"""
        
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
        
    def on_key_event(self, w, e):
        if is_key_control(e):
            self.to_copy = True
        else:
            self.to_copy = False