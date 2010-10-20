'''
Created on Feb 26, 2010

@author: ivan
'''
import os
import urllib

def isDirectory(path):
    return os.path.isdir(path)

def get_file_extenstion(fileName):    
    return os.path.splitext(fileName)[1].lower()

def file_extenstion(file_name):
    return os.path.splitext(file_name)[1].lower()               

def get_file_path_from_dnd_dropped_uri(uri):
    path = ""
    if uri.startswith('file:\\\\\\'): # windows
        path = uri[8:] # 8 is len('file:///')
    elif uri.startswith('file://'): # nautilus, rox
        path = uri[7:] # 7 is len('file://')
    elif uri.startswith('file:'): # xffm
        path = uri[5:] # 5 is len('file:')

    path = urllib.url2pathname(path) # escape special chars
    path = path.strip('\r\n\x00') # remove \r\n and NULL

    return path
