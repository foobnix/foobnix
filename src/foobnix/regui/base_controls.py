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
from foobnix.regui.service.lastfm_service import LastFmService
import thread
from threading import Lock
class BaseFoobnixControls(LoadSave):
    def __init__(self):
        
        self.lastfm = LastFmService()
        self.lock = Lock()
        pass
    
    def search_top_tracks(self, query):
        def in_thread(query):
            results = self.lastfm.search_top_tracks(query)
            self.notetabs.append_tab(query, results)
            self.lock.release()
            self.search_progress.stop()
        
        if self.lock.locked():
            LOG.info("SEARCH NOT FINISHED")
        else:
            self.lock.acquire()
            self.search_progress.start(query)
            thread.start_new_thread(in_thread, (query,))
            
            
            #in_thread(query)

        
    def append_to_notebook(self, text, beans):
        path = beans[0].path
        if os.path.isdir(path):
            scanner = DirectoryScanner(beans[0].path)
            results = scanner.get_music_results()
            results = update_all_id3(results)        
            self.notetabs.append_tab(text, results)
        else:
            self.notetabs.append_tab(text, [beans[0]])
                
    def ass(self, i):
        self.notetabs.append(FModel(i, "3").add_level(None))
        
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
            if isinstance(self.__dict__[element], LoadSave):
                self.__dict__[element].on_load()
            else:
                LOG.debug("NOT LOAD", self.__dict__[element])
        self.window.show()
            
    def on_save(self):
        for element in self.__dict__:
            if isinstance(self.__dict__[element], LoadSave):
                self.__dict__[element].on_save()
            else:
                LOG.debug("NOT SAVE", self.__dict__[element])
