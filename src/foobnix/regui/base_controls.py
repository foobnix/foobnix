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
import os
from foobnix.regui.model import FModel
import thread
import time
class BaseFoobnixControls(LoadSave):
    def __init__(self):
        pass
        
    def append_to_notebook(self, text, beans):
        path = beans[0].path
        if os.path.isdir(path):
            scanner = DirectoryScanner(beans[0].path)
            results = scanner.get_music_results()
            results = update_all_id3(results)        
            self.notetabs.append_tab(text, results)
        else:
            self.notetabs.append_tab(text, [beans[0]])
        
        for i in xrange(10):
            thread.start_new_thread(self.ass,(str(i),))                        
                
    def ass(self,i):
        self.notetabs.append(FModel(i,"3").add_level(None))
        
    def next(self):
        self.notetabs.next()
    
    def prev(self):
        self.notetabs.prev()
    
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
