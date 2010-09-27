#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import gtk
from foobnix.util.fc import FC
from foobnix.util import LOG
from foobnix.regui.state import LoadSave
from foobnix.regui.treeview.scanner import DirectoryScanner
from foobnix.regui.id3 import update_all_id3
class BaseFoobnixControls(LoadSave):
    def __init__(self):
        pass
        
    def append_to_notebook(self, text, beans):
        
        scanner = DirectoryScanner(beans[0].path)
        results = scanner.get_music_results()
        results = update_all_id3(results)
        self.notetabs.append_tab(text, results)
    
    def filter_tree(self, value):
        self.tree.filter(value)
    
    def quit(self, *a):
        LOG.info("Controls - Quit")
        self.on_save()
        FC().save()
        
        gtk.main_quit()
    
    
    def on_load(self):
        for element in self.__dict__:
            self.__dict__[element].on_load()
        self.window.show()
            
    def on_save(self):
        for element in self.__dict__:
            self.__dict__[element].on_save()
