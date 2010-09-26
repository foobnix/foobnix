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
    
    def _scanner(self, path, level):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = self.sort_by_name(path, list)

        for file in list:
            full_path = os.path.join(path, file)
            
            if os.path.isfile(full_path) and file_extenstion(file) not in FC().support_formats:
                continue;
            
            if self.is_dir_with_music(full_path):
                self.results.append(FModel(file, full_path).add_level(level).add_is_file(False))
                self._scanner(full_path, full_path)
            elif os.path.isfile(full_path):
                self.results.append(FModel(file, full_path).add_level(level).add_is_file(True))

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
