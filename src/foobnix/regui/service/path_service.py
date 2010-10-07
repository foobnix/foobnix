#-*- coding: utf-8 -*-
'''
Created on 3 окт. 2010

@author: ivan
'''
import os.path

def get_foobnix_resourse_path_by_name(filename):
    path_tuple = ("/usr/local/share/pixmaps/",\
                  "/usr/share/pixmaps/",\
                  "pixmaps/")
    for x in path_tuple:
        if os.path.exists (x+filename):
            return x+filename
               