#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
import os
"""Music directory scanner"""
class DirectoryScanner():
       
    def __init__(self, path):
        self.path = path
        self.results = []
    
    def get_results(self):
        self._scanner(self.path, None)
        return self.results
    
    def _scanner(self, path, level):
        dir = os.path.abspath(path)
        list = os.listdir(dir)
        list = self.sort_by_name(path, list)

        for file in list:
            full_path = os.path.join(path, file)
            self.results.append(ScannerBean(file, full_path, level))
            if os.path.isdir(full_path):
                self._scanner(full_path, full_path)

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

class ScannerBean():
    def __init__(self, name, path, parent):
        self.name = name
        self.path = path
        self.parent = parent
