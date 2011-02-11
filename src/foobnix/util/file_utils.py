'''
Created on Feb 26, 2010

@author: ivan
'''
import os
import urllib
from foobnix.util.fc import FC
import logging

def open_in_filemanager(path):
    dirname = os.path.dirname(path)
                        
    if os.environ.has_key('DESKTOP_SESSION'):
        for fm in FC().file_managers:
            if os.system(fm + ' \"' + dirname + '\" 2>>/dev/null'):
                continue
            else:
                logging.info("Folder " + dirname + " has been opened in " + fm)
                return
    else:
        os.system('explorer ' + '/"' + dirname + '/"')

def isDirectory(path):
    return os.path.isdir(path)

"""extentsion linke .mp3, .mp4"""
def get_file_extension(fileName):    
    return os.path.splitext(fileName)[1].lower().strip()

def file_extension(file_name):
    return get_file_extension(file_name)

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
