'''
Created on Feb 26, 2010

@author: ivan
'''
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.easyid3 import EasyID3

import os
import LOG
from mutagen import File


class Song:
    
    FOLDER_TYPE = 0
    FILE_TYPE = 1
    URL_TYPE = 2
    
    
    def __init__(self, name, path, type = FILE_TYPE):
        self.name = name
        self.path = path
        
        self.seconds = 0
        
        self.album = ""
        self.artist = ""
        self.title = ""
        self.date = ""
        self.genre = ""
        self.tracknumber = ""
        
        self.type = type
        
        if os.path.isfile(self.path):
            self._getMp3Tags()
            
    def __str__(self):
        return "Song: " + self.path
    
    def getFullDescription(self):
        if self.type!=self.URL_TYPE:
            if self.title and self.artist and self.album:
                return self.artist + " - [" + self.album + "]  #" + self.tracknumber + " " + self.title
            else:
                return self.name
        else:
            return "Radio Playing..."
    
    def getShorDescription(self):
        if self.title and self.album:
            return self.title + " (" + self.album + ")"
        return self.name
                            
               
    def _getMp3Tags(self):
        audio = None
        try:
            audio = MP3(self.path, ID3=EasyID3)
        except HeaderNotFoundError:
            try:
                audio = File(self.path)
            except HeaderNotFoundError:
                pass        
             
        LOG.debug("VALID KEYS" , audio)
        if audio and audio.has_key('album'): self.album = audio["album"][0]
        if audio and audio.has_key('artist'): self.artist = audio["artist"][0]
        if audio and audio.has_key('title'): self.title = audio["title"][0]
        if audio and audio.has_key('date'): self.date = audio["date"][0]
        if audio and audio.has_key('genre'): self.genre = audio["genre"][0]
        if audio and audio.has_key('tracknumber'): self.tracknumber = audio["tracknumber"][0]

                
