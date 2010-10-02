#-*- coding: utf-8 -*-
import gtk
import gobject
from foobnix.regui.treeview.scanner import DirectoryScanner
from foobnix.regui.model import FTreeModel, FModel
from foobnix.util import LOG
import uuid
from foobnix.regui.model.signal import FControl
import copy

class TreeViewControl(gtk.TreeView, FTreeModel, FControl):
    
    def __init__(self, controls):
        gtk.TreeView.__init__(self)           
        FTreeModel.__init__(self)
        FControl.__init__(self, controls)
             
        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.set_enable_tree_lines(True)
        
        """model config"""
        print "types", FTreeModel().types()
        self.model = gtk.TreeStore(*FTreeModel().types())
        
        """filter config"""
        self.filter_model = self.model.filter_new()
        print "visible", self.visible[0]
        self.filter_model.set_visible_column(self.visible[0])
        self.set_model(self.filter_model)    
        
        """connectors"""
        self.connect("button-press-event", self.on_button_press)
        self.connect("key-release-event", self.on_key_release)
        
        #self.connect("drag-data-get", self.drag_data_get_data)
        #self.connect("drag-data-received", self.drag_data_received_data)
        
        
        self.count_index = 0
        
        #self.set_reorderable(True) 
        self.set_headers_visible(False)
        
        self.set_drag_dest_row((0), 0)
        #self.append(FModel("text", "path").add_font("bold"))
    
        #self.connect("drag-data-get", self.on_drag_drop_get)
        #self.connect("drag-drop", self.on_drag_drop)        
        #self.connect("drag-data-received", self.on_drag_received)
        
        
    def on_drag_drop(self, *args):
        print "on_drag_drop"
        print args
    
    def on_drag_drop_get(self, *args):
        print "on_drag_drop_get"     
        print args
        
    def check_sanity(self, model, iter_to_copy, target_iter):
    
        path_of_iter_to_copy = model.get_path(iter_to_copy)
        path_of_target_iter = model.get_path(target_iter)
        if path_of_target_iter[0:len(path_of_iter_to_copy)] == path_of_iter_to_copy:
            return False
        else:
            return True
    
    def iter_copy(self, treeview, model, iter_to_copy, target_iter, pos):
    
        data_column_0 = model.get_value(iter_to_copy, 0)
        data_column_1 = model.get_value(iter_to_copy, 1)
        if (pos == gtk.TREE_VIEW_DROP_INTO_OR_BEFORE) or (pos == gtk.TREE_VIEW_DROP_INTO_OR_AFTER):
            new_iter = model.prepend(target_iter, None)
        elif pos == gtk.TREE_VIEW_DROP_BEFORE:
            new_iter = model.insert_before(None, target_iter)
        elif pos == gtk.TREE_VIEW_DROP_AFTER:
            new_iter = model.insert_after(None, target_iter)
        model.set_value(new_iter, 0, data_column_0)
        model.set_value(new_iter, 1, data_column_1)
        if model.iter_has_child(iter_to_copy):
            for i in range(0, model.iter_n_children(iter_to_copy)):
                next_iter_to_copy = model.iter_nth_child(iter_to_copy, i)
                self.iter_copy(treeview, model, next_iter_to_copy, new_iter, gtk.TREE_VIEW_DROP_INTO_OR_BEFORE)
    
    def on_drag_received(self, treeview, drag_context, x, y, selection, info, eventtime):
        print treeview, drag_context, x, y, selection, info, eventtime
    
        path, pos = treeview.get_dest_row_at_pos(x, y)
        model, iter_to_copy = treeview.get_selection().get_selected()
        target_iter = model.get_iter(path)
        if self.check_sanity(model, iter_to_copy, target_iter):
            self.iter_copy(treeview, model, iter_to_copy, target_iter, pos)
            drag_context.finish(True, True, eventtime)
            treeview.expand_all()
        else:
            drag_context.finish(gtk.FALSE, gtk.FALSE, eventtime)
        
                
    def on_drag_drop(self, *args):
        print args
        

    def set_scrolled(self, policy_horizontal, policy_vertical):        
        self.scroll = gtk.ScrolledWindow()        
        self.scroll.set_policy(policy_horizontal, policy_vertical)
        self.scroll.add_with_viewport(self)
        self.scroll.show_all()
        return self
    
    def populate(self, beans):
        self.clear()
        for bean in beans:
            bean.level = None
            self.append(bean)
                
    def append(self, bean):        
        bean.visible = True        
        """ check append add title and artist"""
        #bean.text = bean.text + " ["+str(bean.artist)+ " - " +str(bean.title) + "]"+str(bean.font)
        #bean.text = bean.text + " !" + str(bean.info)
        #bean.text = bean.text + " !" + str(bean.start_sec) + "=" + str(bean.duration_sec) 
               
        bean.index = self.count_index
        self.count_index += 1
        #bean.play_icon = gtk.STOCK_MEDIA_PLAY
        attributes = []
        m_dict = FTreeModel().cut().__dict__
        new_dict = dict (zip(m_dict.values(), m_dict.keys()))
        
        for key in new_dict.values():
            value = getattr(bean, key)
            attributes.append(value)   
        if isinstance(bean.level, gtk.TreeIter):            
            value = self.model.append(bean.level, attributes)
        else:
            value = self.model.append(None, attributes)
        return value
    
    def append_from_scanner(self, all):
        """copy beans"""
        beans = copy.deepcopy(all)
        
        hash = {None:None}
        for bean in beans:
            if bean is None:
                continue
            bean.visible = True
            if hash.has_key(bean.level):
                level = hash[bean.level]
            else:
                level = None

            if bean.is_file:
                child_level = self.append(bean.add_font("normal").add_level(level))
            else:
                child_level = self.append(bean.add_font("bold").add_level(level))
                
            hash[bean.path] = child_level
    
    def populate_from_scanner(self, beans):
        self.clear()
        self.append_from_scanner(beans)
    
    def clear(self):
        self.count_index = 0
        self.model.clear()
        
    def  on_button_press(self, w, e):
        pass
    
    def  on_key_release(self, w, e):
        pass
    
    def delete_selected(self):
        selection = self.get_selection()
        fm, paths = selection.get_selected_rows()
        path = paths[0]
        path = self.filter_model.convert_path_to_child_path(path)        
        iter = self.model.get_iter(path)
        self.model.remove(iter)
    
    def get_selected_bean(self):
        selection = self.get_selection()
        model, paths = selection.get_selected_rows()
        if not paths:
            return None
        
        return self._get_bean_by_path(paths[0])
    
    def get_children_beans_by_selected(self):
        selection = self.get_selection()
        model, paths = selection.get_selected_rows()
        selected = model.get_iter(paths[0])
        n = model.iter_n_children(selected)
        iterch = model.iter_children(selected)
        
        results = []
        
        for i in xrange(n):
            path = model.get_path(iterch)
            bean = self._get_bean_by_path(path)
            results.append(bean)            
            iterch = model.iter_next(iterch)
        
        return results
    
    def _get_bean_by_path(self, path):
        model = self.model
        LOG.info("Selecte bean path", path)
        
        path = self.filter_model.convert_path_to_child_path(path)
        LOG.info("Selecte bean path", path)        
        iter = model.get_iter(path)
        
        if iter:
            bean = FModel()
            dt = FTreeModel().__dict__
            for key in dt.keys():
                setattr(bean, key, model.get_value(iter, dt[key][0]))            
            return bean
        return None
    
    def get_bean_by_position(self, position):
        bean = FModel()
        dt = FTreeModel().__dict__
        for key in dt.keys():
            setattr(bean, key, self.model[position][dt[key][0]])
        
        return bean       

    def get_all_beans(self):
        beans = []
        for i in xrange(len(self.model)):
            beans.append(self.get_bean_by_position(i))
        return beans
            
    def get_all_selected_beans(self):
        selection = self.get_selection()
        model, paths = selection.get_selected_rows()
        if not paths:
            return None
        beans = []
        for path in paths:       
            selection.select_path(path)     
            bean = self._get_bean_by_path(path)
            beans.append(bean)
        return beans
    
    def filter(self, query):        
        if len(query.strip()) > 0:
            query = query.strip().decode("utf-8").lower()
            
            for line in self.model:
                name = line[self.text[0]].lower()

                if name.find(query) >= 0:
                    #LOG.info("FIND PARENT:", name, query)
                    line[self.visible[0]] = True                    
                else:
                    find = False
                    child_count = 0;
                    for child in line.iterchildren():
                        name = str(child[self.text[0]]).decode("utf-8").lower()
                        #name = child[self.text[0]]
                        if name.find(query) >= 0:
                            child_count += 1
                            #LOG.info("FIND CHILD :", name, query)
                            child[self.visible[0]] = True
                            line[self.visible[0]] = True
                            #line[self.POS_FILTER_CHILD_COUNT] = child_count 
                            find = True                            
                        else:
                            child[self.visible[0]] = False
                    if not find:
                        line[self.visible[0]] = False
                    else:
                        self.expand_all()                                           
        else:
            self.collapse_all()
            for line in self.model:                
                line[self.visible[0]] = True
                for child in line.iterchildren():
                    child[self.visible[0]] = True
