#-*- coding: utf-8 -*-
'''
Created on 20 окт. 2010

@author: ivan
'''

import gtk
from foobnix.regui.model import FTreeModel, FModel
from foobnix.regui.model.signal import FControl
from random import randint
from foobnix.regui.treeview.filter_tree import FilterTreeControls
import logging
import gobject

class CommonTreeControl(FTreeModel, FControl, FilterTreeControls):

    def __init__(self, controls):        
        FilterTreeControls.__init__(self, controls)
        
        FTreeModel.__init__(self)
        FControl.__init__(self, controls)

        self.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.set_enable_tree_lines(True)

        """model config"""
        self.model = gtk.TreeStore(*FTreeModel().types())

        """filter config"""
        self.filter_model = self.model.filter_new()
        self.filter_model.set_visible_column(self.visible[0])
        self.set_model(self.filter_model)

        """connectors"""
        self.connect("button-press-event", self.on_button_press)
        self.connect("key-release-event", self.on_key_release)
        self.connect("row-expanded", self.on_row_expanded)
        self.connect('button_press_event', self.on_multi_button_press)
        self.connect('button_release_event', self.on_multi_button_release)

        self.count_index = 0

        self.set_reorderable(False)
        self.set_headers_visible(False)

        self.set_type_plain()
        
        self.active_UUID = -1
        
        
        self.defer_select = False
        
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self)
    
    def on_row_expanded(self, widget, iter, path):
        bean = self.get_bean_from_path(path)
        self.on_bean_expanded(bean)
    
    def get_bean_from_path(self, path_string):
        iter = self.model.get_iter(path_string)
        return self.get_bean_from_iter(iter)
    
    def on_bean_expanded(self, bean):
        pass
    
    def on_multi_button_press(self, widget, event):
        target = self.get_path_at_pos(int(event.x), int(event.y))
        if (target and event.type == gtk.gdk.BUTTON_PRESS and not (event.state & (gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK)) #@UndefinedVariable
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
        def task():
            self._populate_all(beans)
            
        gobject.idle_add(task)
        
    def _populate_all(self, beans):
        self.clear_tree()
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

    def get_previous_iter(self, model, iter):
        path = model.get_path(iter)
        if path[-1] != 0:
            previous_path = path[:-1] + (path[-1] - 1,)
            return model.get_iter(previous_path) 
    
    def get_iter_from_row_reference(self, row_reference):
        model = row_reference.get_model()
        path = row_reference.get_path()
        return model.get_iter(path)
    
    def get_row_reference_from_iter(self, model, iter):
        path = model.get_path(iter)
        return gtk.TreeRowReference(model, path)
    
    def clear_tree(self):
        self.model.clear()

    def on_button_press(self, w, e):
        pass

    def on_key_release(self, w, e):
        pass

    def delete_selected(self):
        selection = self.get_selection()
        fm, paths = selection.get_selected_rows()
        paths.reverse()
        for path in paths:
            path = self.filter_model.convert_path_to_child_path(path)
            iter = self.model.get_iter(path)
            self.model.remove(iter)
        
        if len(paths) == 1:
            path = paths[0]
            logging.debug("path " + repr(path))
            position = path[0]
            selection.select_path(position - 1)

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
    
    def get_selected_beans(self):
        paths = self.get_selected_bean_paths()
        if not paths:
            return None
        
        beans = [self._get_bean_by_path(path) for path in paths]
                
        return beans
    
    def get_selected_or_current_bean(self):
        bean = self.get_selected_bean()  
        if bean:
            return bean
        else:              
            return self.get_current_bean_by_UUID();
    
    def set_play_icon_to_bean_to_selected(self):
        
        for row in self.model:
            row[self.play_icon[0]] = None
        
        paths = self.get_selected_bean_paths()
        if not paths:
            return None
        
        path = paths[0]  
                 
        iter = self.model.get_iter(path)
        self.model.set_value(iter, FTreeModel().play_icon[0], gtk.STOCK_GO_FORWARD)
        self.active_UUID = self.model.get_value(iter, FTreeModel().UUID[0])
        
    def set_bean_column_value(self, bean, colum_num, value):
        for row in self.model:
            if row[self.UUID[0]] == bean.UUID:
                row[colum_num] = value
                break
              
    def update_bean(self, bean):
        for row in self.model:
            if row[self.UUID[0]] == bean.UUID:
                dict = FTreeModel().__dict__
                for key in dict:
                    value = getattr(bean, key)
                    row_num = dict[key][0]
                    row[row_num] = value
                break
        
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
    
    def set_play_icon_to_bean(self, bean):
        def task():
            for row in self.model:
                if row[self.UUID[0]] == bean.UUID:
                    row[self.play_icon[0]] = gtk.STOCK_GO_FORWARD
                    self.active_UUID = bean.UUID                
                else:
                    row[self.play_icon[0]] = None
        #gobject.idle_add(task)
        task()

    def get_next_bean_by_UUID(self, repeat_all=False):
        '''not correct method after rebuild beans'''
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
        '''not correct method after rebuild beans'''
        UUID = self.active_UUID        
        rows = self.get_all_file_rows() 
        
        for i, row in enumerate(rows):
            if row[self.UUID[0]] == UUID and i > 0:
                prev_row = rows[i - 1]
                if prev_row: 
                    return self.get_bean_from_row(prev_row)
        
        if repeat_all:
            return self.get_bean_from_row(rows[len(rows) - 1])
        
    def get_next_bean(self, repeat_all=False):
        rows = self.get_all_file_rows()
        for i, row in enumerate(rows):
            if row[self.play_icon[0]] and i + 1 < len(rows):
                next_row = rows[i + 1]
                if next_row:
                    return self.get_bean_from_row(next_row)
        
        if repeat_all:
            return self.get_bean_from_row(rows[0])
    
    def get_prev_bean(self, repeat_all=False):
        rows = self.get_all_file_rows() 
        for i, row in enumerate(rows):
            if row[self.play_icon[0]] and i > 0:
                prev_row = rows[i - 1]
                if prev_row: 
                    return self.get_bean_from_row(prev_row)
        
        if repeat_all:
            return self.get_bean_from_row(rows[len(rows) - 1])
        
    def get_all_file_rows(self):
        rows = [row for row in self.model if row[self.is_file[0]]]
        return rows

    def get_random_bean(self):        
        rows = self.get_all_file_rows()
        return self.get_bean_from_row(rows[randint(0, len(rows) - 1)])
    
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
            if model and paths:
                iter = model.get_iter(paths[0])
                return self.get_child_beans_by_parent(model, iter)
            return None
     
    def get_all_beans(self):
        results = []
        next = self.model.get_iter_first()
        
        if next:
            parent = self.get_bean_from_iter(next) 
            results += [parent] + self.get_child_beans_by_parent(self.model, next)
        else:
            return None
        
        flag = True
                
        while flag:
            next = self.model.iter_next(next)
            if not next:
                flag = False
            else:
                parent = self.get_bean_from_iter(next) 
                results += [parent] + self.get_child_beans_by_parent(self.model, next)
                
        return results
    
    def get_all_beans_text(self):
        result = []
        beans = self.get_all_beans()
        
        if not beans:
            return result
        
        for bean in beans:
            result.append(bean.text)
                            
        return result
                
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

    def select_paths(self, paths):
        selection = self.get_selection()
        for path in paths:
            self.expand_to_path(path)
            selection.select_path(path)

    def restore_selection(self, paths):        
        self.select_paths(paths)

    def restore_expand(self, paths):
        for path in paths:
            self.expand_to_path(path)
    
    def copy_info_to_clipboard(self, mode=False):
        beans = self.get_selected_beans()
        if not beans:
            return
        clb = gtk.Clipboard()
        if not mode:
            tracks = [b.tracknumber + ". " + b.title + " (" + b.time + ")" 
                      if (b.tracknumber and b.title and b.time) else b.text for b in beans]
        else:
            tracks = []
            for bean in beans:
                artist = bean.artist if bean.artist else "Unknown artist"
                title = bean.title if bean.title else "Unknown title"
                album = bean.album if bean.album else "Unknown album"
                tracks.append(artist + " - " + title + " (" + album + ")")
                
        clb.set_text("\n".join(tracks))
                
        
    def selection_changed(self, callback):
        def on_selection_changed(w):
            paths = self.get_selected_bean_paths()
            if paths != None:
                callback(paths)
        selection = self.get_selection()
        selection.connect("changed", on_selection_changed)
    
    def expand_updated(self, callback):
        def on_expand_collapse(w, iter, path):
            values = []
            self.map_expanded_rows(lambda w, p : values.append(p))
            callback(values)
        self.connect("row-expanded", on_expand_collapse)
        self.connect("row-collapsed", on_expand_collapse)
