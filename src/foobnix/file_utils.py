'''
Created on Feb 26, 2010

@author: ivan
'''
import os
from foobnix.util import LOG
import song
from song import Song
from confguration import FConfiguration

def isDirectory(path):
    return os.path.isdir(path)

def getExtenstion(fileName):
    return fileName[-4:].lower()

def getSongFromWidget(widget, name_pos, path_pos):
    selection = widget.get_selection()
    model, selected = selection.get_selected()
    if selected:
        song_name = model.get_value(selected, name_pos)
        song_path = model.get_value(selected, path_pos)                
    
    return Song(song_name, song_path)                   

def getSongPosition(song, songs):
    if not songs:
        return - 1
    for i in range(len(songs)):
        tempSong = songs[i]
        if tempSong.path == song.path:
            return i                
    return - 1


