'''
Created on Feb 26, 2010

@author: ivan
'''
import os
import urllib
from foobnix.util.fc import FC
import logging

def open_in_filemanager(path, managers=None):
    dirname = os.path.dirname(path)
    if FC().active_manager[0] and not managers:
        managers = [FC().active_manager[1]]
    else:
        managers = FC().file_managers
    
    def search_mgr(managers):
        if os.environ.has_key('DESKTOP_SESSION'):
            for fm in managers:
                if os.system(fm + ' \"' + dirname + '\" 2>>/dev/null'):
                    continue
                else:
                    logging.info("Folder " + dirname + " has been opened in " + fm)
                    return True
        else:
            if not os.system('explorer ' + '/"' + dirname + '/"'):
                logging.info("Folder " + dirname + " has been opened in explorer")
                return True
    
    if not search_mgr(managers):
        if FC().active_manager[0]:
            logging.warning(FC().active_manager[1] + "not installed in system")
            logging.info("Try open other file manager")
            if not search_mgr(FC().file_managers):
                logging.warning("None file manager found")
        else:
            logging.warning("None file manager found")          
    
                
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
