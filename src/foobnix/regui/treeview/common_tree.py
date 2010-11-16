#-*- coding: utf-8 -*-
'''
Created on 20 окт. 2010

@author: ivan
'''

import gtk
from foobnix.regui.model import FTreeModel, FModel
from foobnix.regui.model.signal import FControl
from foobnix.regui.treeview.drugdrop_tree import DrugDropTree
from random import randint
import gobject
from foobnix.regui.treeview.filter_tree import FilterTreeControls


class CommonTreeControl(DrugDropTree, FTreeModel, FControl, FilterTreeControls):

    def __init__(self, controls):        
        DrugDropTree.__init__(self, controls)
        
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

        self.count_index = 0

        self.set_reorderable(False)
        self.set_headers_visible(False)

        self.set_type_plain()
        
        self.active_UUID = -1
        
        self.connect('button_press_event', self.on_multi_button_press)
        self.connect('button_release_event', self.on_multi_button_release)
        self.defer_select = False
        
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self)
        
    def on_multi_button_press(self, widget, event):
        target = self.get_path_at_pos(int(event.x), int(event.y))
        if (target and event.type == gtk.gdk.BUTTON_PRESS and not (event.state & (gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK)) 
            and self.get_selection().path_is_selected(target[0])):
            # disable selection
            self.get_selection().set_select_function(lambda * ignore: False)
            self.defer_select = target[0]
        
    def on_multi_button_release(self, widget, event):
        self.get_selection().set_select_function(lambda * ignore: True)
        
        target = self.get_path_at_pos(int(event.x), int(event.y))
        if (self.defer_select and target and self.defer_select == target[0] and not (event.x == 0 and event.y == 0)): # certain drag and drop
            self.set_cursor(target[0], target[1], False)
        
        self.defer_select = False
    
    def rename_selected(self, text):
        selection = self.get_selection()
        fm, paths = selection.get_selected_rows()
        path = paths[0]
        path = self.filter_model.convert_path_to_child_path(path)        
        iter = self.model.get_iter(path)
        
        self.model.set_value(iter, self.text[0], text)
        
    
    def populate(self, bean):
        self.clear()
        self.append(bean)
        
    def populate_all(self, beans):
        print "populate all", self.current_view
        self.clear()
        self.append_all(beans)
    
    def get_bean_from_iter(self, iter):
        return self.get_bean_from_model_iter(self.model, iter)

    
    def get_bean_from_row(self, row):
        bean = FModel()
        id_dict = FTreeModel().cut().__dict__
        for key in id_dict.keys():
            num = id_dict[key]
            setattr(bean, key, row[num])
        return bean


    def get_row_from_bean(self, bean):
        attributes = []
        m_dict = FTreeModel().cut().__dict__
        new_dict = dict (zip(m_dict.values(), m_dict.keys()))

        for key in new_dict.values():
            value = getattr(bean, key)
            attributes.append(value)
        return attributes

    def get_row_from_model_iter(self, model, iter):
        attributes = []
        size = len(FTreeModel().__dict__)
        for i in xrange(size):
            value = model.get_value(iter, i)
            attributes.append(value)
        return attributes

    def clear(self):
        print "clean"
        gobject.idle_add(self.model.clear)
        #self.model.clear()

        

    def on_button_press(self, w, e):
        pass

    def on_key_release(self, w, e):
        pass

    def delete_selected(self):
        selection = self.get_selection()
        fm, paths = selection.get_selected_rows()
        
        to_delete = []
        for path in paths:
            path = self.filter_model.convert_path_to_child_path(path)
            iter = self.model.get_iter(path)
            to_delete.append(iter)

        def task():        
            for iter in to_delete:
                self.model.remove(iter)
        gobject.idle_add(task)

    def get_selected_bean_paths(self):
        selection = self.get_selection()
        if not selection:
            return None
        model, paths = selection.get_selected_rows()
        if not paths:
            return None
        return paths
        
    
    def get_selected_bean(self):
        paths = self.get_selected_bean_paths()
        if not paths:
            return None
        selected_bean = self._get_bean_by_path(paths[0])
        return selected_bean
    
    def set_play_icon_to_bean_to_selected(self):
        def task():
            for row in self.model:
                row[self.play_icon[0]] = None
            
            paths = self.get_selected_bean_paths()
            if not paths:
                return None
            
            path = paths[0]  
                     
            iter = self.model.get_iter(path)
            self.model.set_value(iter, FTreeModel().play_icon[0], gtk.STOCK_GO_FORWARD)
            self.active_UUID = self.model.get_value(iter, FTreeModel().UUID[0])
        
        gobject.idle_add(task)
        
    def set_bean_column_value(self, bean, colum_num, value):
        def task():
            for row in self.model:
                if row[self.UUID[0]] == bean.UUID:
                    row[colum_num] = value
                    break
        gobject.idle_add(task)
            
    def update_bean(self, bean):
        def task():
            for row in self.model:
                if row[self.UUID[0]] == bean.UUID:
                    dict = FTreeModel().__dict__
                    for key in dict:
                        value = getattr(bean, key)
                        row_num = dict[key][0]
                        row[row_num] = value
                    break
        gobject.idle_add(task)
        
        
    def set_play_icon_to_bean(self, bean):
        def task():
            for row in self.model:
                if row[self.UUID[0]] == bean.UUID:
                    row[self.play_icon[0]] = gtk.STOCK_GO_FORWARD
                    self.active_UUID = bean.UUID                
                else:
                    row[self.play_icon[0]] = None
        gobject.idle_add(task)
        
    def _get_bean_by_path(self, path):
        model = self.model
        path = self.filter_model.convert_path_to_child_path(path)
        iter = model.get_iter(path)

        if iter:
            bean = FModel()
            dt = FTreeModel().__dict__
            for key in dt.keys():
                setattr(bean, key, model.get_value(iter, dt[key][0]))
            return bean
        return None

    def get_bean_by_UUID(self, UUID):
        for row in self.model:
            if row[self.UUID[0]] == UUID:
                return self.get_bean_from_row(row)        
            
    def get_current_bean_by_UUID(self):
        UUID = self.active_UUID
        for row in self.model:
            if row[self.UUID[0]] == UUID:               
                return self.get_bean_from_row(row)
                        
        return None
        

    def get_next_bean_by_UUID(self, repeat_all=False):
        UUID = self.active_UUID
        rows = self.get_all_file_rows()
        
        for i, row in enumerate(rows):
            if row[self.UUID[0]] == UUID and i + 1 < len(rows):
                next_row = rows[i + 1]
                if next_row:
                    return self.get_bean_from_row(next_row)
        
        if repeat_all:
            return self.get_bean_from_row(rows[0])
        
    def get_prev_bean_by_UUID(self, repeat_all=False):
        UUID = self.active_UUID        
        rows = self.get_all_file_rows() 
        
        for i, row in enumerate(rows):
            if row[self.UUID[0]] == UUID and i > 0:
                prev_row = rows[i - 1]
                if prev_row: 
                    return self.get_bean_from_row(prev_row)
        
        if repeat_all:
            return self.get_bean_from_row(rows[len(rows) - 1])
        

    def get_all_file_rows(self):
        rows = []
        for row in self.model:
            if row[self.is_file[0]]:
                rows.append(row)
        
        return rows

    def get_random_bean(self):        
        rows = self.get_all_file_rows()
        return self.get_bean_from_row(rows[randint(0, len(rows))])
    
    def get_child_level1_beans_by_selected(self):
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
    
    def get_all_child_beans_by_selected(self):
            model, paths = self.get_selection().get_selected_rows()
            #to_path = model.convert_path_to_child_path(paths[0])
            iter = model.get_iter(paths[0])
            return self.get_child_iters_by_parent(model, iter)
     
    def get_all_beans(self):
        results = []
        next = self.model.get_iter_first()
        
        if next:
            parent = self.get_bean_from_iter(next) 
            results += [parent] + self.get_child_iters_by_parent(self.model, next)
        else:
            return None
        
        flag = True
                
        while flag:
            next = self.model.iter_next(next)
            if not next:
                flag = False
            else:
                parent = self.get_bean_from_iter(next) 
                results += [parent] + self.get_child_iters_by_parent(self.model, next)
                
        return results
                
    def get_child_iters_by_parent(self, model, iter):
        list = []
        if model.iter_has_child(iter):
            for i in xrange(model.iter_n_children(iter)):
                next_iter = model.iter_nth_child(iter, i)
                
                parent = self.get_bean_from_model_iter(model, next_iter)                
                list.append(parent)
                 
                beans = self.get_child_iters_by_parent(model, next_iter)
                
                for bean in beans:
                    bean.parent(parent)                
                    list.append(bean)
                
        return list
                
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
