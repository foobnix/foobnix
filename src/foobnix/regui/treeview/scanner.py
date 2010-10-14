#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import os
from foobnix.util.fc import FC
from foobnix.util.file_utils import file_extenstion
from foobnix.util import LOG
from foobnix.regui.model import FModel

"""Music directory scanner"""
class DirectoryScanner():
       
    def __init__(self, path):
        self.path = path 
        self.results = []
    
    def get_music_results(self):
        self._scanner(self.path, None)
        return self.results
    
    def get_music_file_results(self):        
        self._scanner(self.path, None)
        all = []
        for file in self.results:
            if file.is_file:
                all.append(file)
        return all
    
    def _scanner(self, path, level):
        if not os.path.exists(path):
            return None
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = self.sort_by_name(path, list)

        for file in list:
            full_path = os.path.join(path, file)
            
            if os.path.isfile(full_path) and file_extenstion(file) not in FC().support_formats:
                continue;
            
            if self.is_dir_with_music(full_path):
                b_bean = FModel(file, full_path).add_parent(level).add_is_file(False)
                self.results.append(b_bean)
                self._scanner(full_path, b_bean.get_level())
            elif os.path.isfile(full_path):
                self.results.append(FModel(file, full_path).add_parent(level).add_is_file(True))

    def sort_by_name(self, path, list):
        files = []
        directories = []
        for file in list:
            full_path = os.path.join(path, file)
            if os.path.isdir(full_path):
                directories.append(file)
            else:
                files.append(file)

        return sorted(directories) + sorted(files)
    
    def is_dir_with_music(self, path):
        if os.path.isdir(path):
            list = None
            try:
                list = os.listdir(path)
            except OSError, e:
                LOG.info("Can'r get list of dir", e)

            if not list:
                return False

            for file in list:
                full_path = os.path.join(path, file)
                if os.path.isdir(full_path):
                    if self.is_dir_with_music(full_path):
                        return True
                else:
                    if file_extenstion(file) in FC().support_formats:
                        return True
        return False  
