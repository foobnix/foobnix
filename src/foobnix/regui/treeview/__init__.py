#-*- coding: utf-8 -*-
import gtk
import gobject
from foobnix.regui.treeview.scanner import DirectoryScanner
from foobnix.regui.model import FTreeModel, FModel
from foobnix.util import LOG
import uuid
from foobnix.regui.model.signal import FControl

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
        filter = self.model.filter_new()
        print "visible", self.visible[0]
        filter.set_visible_column(self.visible[0])
        self.set_model(filter)    
        
        """connectors"""
        self.connect("button-press-event", self.on_button_press)
        self.connect("key-release-event", self.on_key_release)
        
        self.count_index = 0
        #self.append(FModel("text", "path").add_font("bold"))
        
       
    
    def set_scrolled(self, policy_horizontal, policy_vertical):        
        self.scroll = gtk.ScrolledWindow()        
        self.scroll.set_policy(policy_horizontal, policy_vertical)
        self.scroll.add_with_viewport(self)
        self.scroll.show_all()
        return self
    
    def populate(self, beans):
        self.model.clear()
        for bean in beans:
            bean.level = None
            self.append(bean)
                
    def append(self, bean):        
        bean.visible = True        
        """ check append add title and artist"""
        #bean.text = bean.text + " ["+str(bean.artist)+ " - " +str(bean.title) + "]"+str(bean.font)
        #bean.text = bean.text + " !" + str(bean.info)
        bean.text = bean.text + " !" + str(bean.start_sec) + "=" + str(bean.duration_sec) 
               
        bean.index = self.count_index
        self.count_index += 1
        #bean.play_icon = gtk.STOCK_MEDIA_PLAY
        attributes = []
        m_dict = FTreeModel().cut().__dict__
        new_dict = dict (zip(m_dict.values(), m_dict.keys()))
        
        for key in new_dict.values():
            value = getattr(bean, key)
            attributes.append(value)   
        
        #gtk.gdk.threads_enter() #@UndefinedVariable
        with gtk.gdk.lock:
            value = self.model.append(bean.level, attributes)
        #gtk.gdk.threads_leave() #@UndefinedVariable 
        return value
    
    def populate_from_scanner(self, beans):
        self.model.clear()
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
    
    def clear(self):
        self.model.clear()
        
    def  on_button_press(self, w, e):
        pass
    
    def  on_key_release(self, w, e):
        pass
    
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
