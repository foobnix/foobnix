#-*- coding: utf-8 -*-
import gtk
import gobject
from foobnix.regui.treeview.scanner import DirectoryScanner
from foobnix.regui.model import FTreeModel, FModel
from foobnix.util import LOG
import uuid

class TreeViewControl(gtk.TreeView, FTreeModel):
    
    def __init__(self):
        gtk.TreeView.__init__(self)   
        FTreeModel.__init__(self)
             
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
        
        #self.append(FModel("1", "2"))
        #scan = DirectoryScanner("/home/ivan/Музыка")
        #self.populate_from_scanner(scan.get_music_results())
        self.count_index = 0
        
    def append(self, bean):        
        bean.visible = True
        
        self.count_index +=1
        bean.index = self.count_index
        #bean.play_icon = gtk.STOCK_MEDIA_PLAY
        attributes = []
        m_dict = FTreeModel().cut().__dict__
        new_dict = dict (zip(m_dict.values(), m_dict.keys()))
        
        for key in new_dict.values():
            value = getattr(bean, key)
            attributes.append(value)        
        return self.model.append(bean.level, attributes)
    
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
        LOG.info("Filter", query)
        if not query:
            """show alll"""
            for line in self.model:                
                line[self.visible[0]] = True
                for child in line.iterchildren():
                    child[self.visible[0]] = True
            self.collapse_all()
            return True

        """filter selected"""        
        query = query.lower()       
        for line in self.model:
            name = line[self.text[0]].lower()

            if name.find(query) >= 0:
                LOG.info("FILTER FIND PARENT:", name, query)
                line[self.visible[0]] = True
                self.expand_all()                    
            else:
                line[self.visible[0]] = False