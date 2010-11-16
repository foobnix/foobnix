#-*- coding: utf-8 -*-
'''
Created on 3 окт. 2010

@author: ivan
'''
import os.path, sys
from foobnix.util import LOG

def get_foobnix_resourse_path_by_name(filename):
    paths = ("/usr/local/share/pixmaps",
             "/usr/share/pixmaps",
             "pixmaps",
             "foobnix/pixmaps",
             "./../../..",
             "./../../",
             "./../pixmaps",
             "./",
             sys.path[1],
             filename)
    for path in paths:
        full_path = os.path.join(path, filename)
        if os.path.isfile(full_path):
            return full_path
    
    LOG.error("******* WARNING: File " + filename + " not found *******")
    raise TypeError, "******* WARNING: File " + filename + " not found *******"
