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
        if getExtenstion(file_name) not in ".mp3, .ogg":
                continue
                    
        full_path = path + "/" + file_name
        
        if not isDirectory(full_path):                                
            result.append(Song(file_name, full_path))
            
    LOG.debug(result)
    return result

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
    for i in range(len(songs)):
        tempSong = songs[i]
        if tempSong.path == song.path:
            return i                
    return 0


