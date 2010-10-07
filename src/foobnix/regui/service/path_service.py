#-*- coding: utf-8 -*-
'''
Created on 3 окт. 2010

@author: ivan
'''
import os.path

def get_foobnix_resourse_path_by_name(filename):
    paths = ("/usr/local/share/pixmaps",\
             "/usr/share/pixmaps",\
             "pixmaps",\
             "./../../..",\
             "./../../",\
             "./")
    for path in paths:
        full_path = os.path.join(path, filename)
        if os.path.exists (full_path):
            return full_path
