#-*- coding: utf-8 -*-
'''
Created on 23 сент. 2010

@author: ivan
'''
import pickle
from foobnix.util import LOG
import os
from foobnix.util.singleton import Singleton

"""Foobnix configuration"""
class FC:
    __metaclass__ = Singleton
    def __init__(self):        
        """init default values"""                    
        self.is_view_info_panel = False
        self.is_view_search_panel = False
        self.is_view_music_tree_panel = True
        
        """player controls"""
        self.volume = 10
        
        """tabs"""
        self.len_of_tab = 30
        self.tab_close_element = "label"
        self.count_of_tabs = 5
        
        """main window controls"""
        self.main_window_size = None
        
        self = self._load();
        
    def save(self):
        FCHelper().save(self)        
    
    def _load(self):
        """restore from file"""
        object = FCHelper().load()
        
        object.__dict__.update(object.__dict__)
        return object
        
        if object:
            dict = object.__dict__
            for i in dict:
                try:
                    if self.__dict__[i]:                 
                        #self.__dict__[i] = dict[i]
                        setattr(self, i, dict[i])
                        print "SET", i, dict[i]
                except Exception, e:
                    LOG.warn("Value not found", e)
                    return False
        return True         
    
    def info(self):
        FCHelper().print_info(self)
    
    def delete(self):
        FCHelper().delete()

CONFIG_FILE = "/tmp/foobnix.pkl"    
    
    
class FCHelper():
    def __init__(self):
        pass
    
    def save(self, object):
        save_file = file(CONFIG_FILE, 'w')
        try:
            pickle.dump(object, save_file)
        except Exception, e:
            LOG.error("Erorr dumping pickle conf", e)
        save_file.close()
        LOG.debug("Config save")
        self.print_info(object);
        
        
    def load(self):
        if not os.path.exists(CONFIG_FILE):
            LOG.warn("Config file not found", CONFIG_FILE)
            return None
        
        with file(CONFIG_FILE, 'r') as load_file:
            try:
                load_file = file(CONFIG_FILE, 'r')
                pickled = load_file.read()            
                
                object = pickle.loads(pickled)
                LOG.debug("Config loaded")
                self.print_info(object);
                return object
            except Exception, e:
                LOG.error("Error laod config", e)
        return None
            
    
    def delete(self):
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
            
    def print_info(self, object):
        dict = object.__dict__
        for i in object.__dict__:
            LOG.debug(i, str(dict[i])[:500]);

c = FC()
print c.main_window_size
c.info()
#setattr(a, all, [1, 2, 3], typecast=typecast)
#a.__setattr__['all'] = [1, 2, 3]
#print a.__dict__
