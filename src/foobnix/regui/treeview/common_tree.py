#-*- coding: utf-8 -*-
'''
Created on 20 окт. 2010

@author: ivan
'''
#-*- coding: utf-8 -*-
import gtk
from foobnix.regui.model import FTreeModel, FModel
from foobnix.util import LOG
from foobnix.regui.model.signal import FControl
from foobnix.regui.treeview.drugdrop_tree import DrugDropTree
from random import randint


class CommonTreeControl(DrugDropTree, FTreeModel, FControl):

    def __init__(self, controls):        
        DrugDropTree.__init__(self,controls)
        
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
    
    def rename_selected(self, text):
        selection = self.get_selection()
        fm, paths = selection.get_selected_rows()
        path = paths[0]
        path = self.filter_model.convert_path_to_child_path(path)        
        iter = self.model.get_iter(path)
        
        gtk.gdk.threads_enter()
        self.model.set_value(iter, self.text[0], text)
        gtk.gdk.threads_leave()
    
    def populate(self, bean):
        self.clear()
        self.append(bean)
        
    def populate_all(self, beans):
        print "populate all", self.current_view
        self.clear()
        self.append_all(beans)
        
    def set_scrolled(self, policy_horizontal, policy_vertical):
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(policy_horizontal, policy_vertical)
        self.scroll.add_with_viewport(self)
        self.scroll.show_all()
        return self

    def get_bean_from_iter(self, iter):
        return self.get_bean_from_model_iter(self.model, iter)

    def get_bean_from_model_iter(self, model, iter):
        bean = FModel()
        id_dict = FTreeModel().cut().__dict__
        for key in id_dict.keys():
            num = id_dict[key]
            val = model.get_value(iter, num)
            setattr(bean, key, val)
        return bean
    
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
        self.count_index = 0
        
        gtk.gdk.threads_enter()
        self.model.clear()
        gtk.gdk.threads_leave()

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
        
        for iter in to_delete: 
            gtk.gdk.threads_enter()
            self.model.remove(iter)
            gtk.gdk.threads_leave()

    def get_selected_bean(self):
        selection = self.get_selection()
        model, paths = selection.get_selected_rows()
        if not paths:
            return None
        selected_bean = self._get_bean_by_path(paths[0])
        print "Selected bean", selected_bean
        return selected_bean

    def set_play_icon_to_bean(self, bean):
        for row in self.model:
            if row[self.UUID[0]] == bean.UUID:
                row[self.play_icon[0]] = gtk.STOCK_MEDIA_PLAY
            else:
                row[self.play_icon[0]] = None

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

    def get_bean_by_UUID(self, UUID):
        for row in self.model:
            if row[self.UUID[0]] == UUID:
                return self.get_bean_from_row(row)        

    def get_next_bean_by_UUID(self, UUID):
        for i, row in enumerate(self.model):
            if row[self.UUID[0]] == UUID:
                if i + 1 < len(self.model):
                    next_row = self.model[i + 1]
                    return self.get_bean_from_row(next_row)                
        return self.get_bean_from_row(self.model[0])
    
    def get_prev_bean_by_UUID(self, UUID):
        for i, row in enumerate(self.model):
            if row[self.UUID[0]] == UUID:
                return self.get_bean_from_row(self.model[i - 1])
        return self.get_bean_from_row(self.model[0])
    
    def get_random_bean(self):        
        return self.get_bean_from_row(self.model[randint(0, len(self.model))])
    
    def get_all_child_beans_by_selected(self):
            filter_model, paths = self.get_selection().get_selected_rows()
            model = filter_model.get_model()
            iter = model.get_iter(paths[0])
            return self.get_child_iters_by_parent(iter)
     
    def get_all_beans(self):
        results = []
        next = self.model.get_iter_first()
        
        if next:
            parent = self.get_bean_from_iter(next) 
            results += [parent] + self.get_child_iters_by_parent(next)
        else:
            return None
        
        flag = True
                
        while flag:
            next = self.model.iter_next(next)
            if not next:
                flag = False
            else:
                parent = self.get_bean_from_iter(next) 
                results += [parent] + self.get_child_iters_by_parent(next)
                
        return results
                
    def get_child_iters_by_parent(self, iter):
        list = []
        if self.model.iter_has_child(iter):
            for i in range(0, self.model.iter_n_children(iter)):
                next_iter = self.model.iter_nth_child(iter, i)
                
                parent = self.get_bean_from_iter(next_iter)                
                list.append(parent)
                 
                beans = self.get_child_iters_by_parent(next_iter)
                
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
