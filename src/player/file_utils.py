'''
Created on Feb 26, 2010

@author: ivan
'''
import os
import LOG
import song
from song import Song

def isDirectory(path):
    return os.path.isdir(path)

def getAllSongsByDirectory(path):
    dir = os.path.abspath(path)
    list = os.listdir(dir)
    result = []            
    for file_name in list:        
        full_path = path + "/" + file_name
        
        if not isDirectory(full_path):                                
            result.append(Song(file_name, full_path))
            
    LOG.debug(result)
    return result

def getSongFromWidget(widget):
    selection = widget.get_selection()
    model, selected = selection.get_selected()
    if selected:
        song_name = model.get_value(selected, 0)
        song_path = model.get_value(selected, 1)                
    
    return Song(song_name, song_path)                   
