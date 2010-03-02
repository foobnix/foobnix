'''
Created on Feb 26, 2010

@author: ivan
'''
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen.easyid3 import EasyID3

import os
import LOG

class Song:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        
        self.album = ""
        self.artist = ""
        self.title = ""
        self.date = ""
        self.genre = ""
        self.tracknumber = ""
        if os.path.isfile(self.path):
            self._getMp3Tags()
            
    def __str__(self):
        return "Song: " + self.path
    
    def getFullDescription(self):
        if self.title and self.artist and self.album:
            return self.artist + " - [" + self.album + "]  #" + self.tracknumber + " " + self.title
        else:
            return self.name
    
    def getShorDescription(self):
        if self.title and self.album:
            return self.tracknumber + " " + self.title + " (" + self.album + ")"
        return self.name
                            
               
    def _getMp3Tags(self):
        if self.path[-4:].lower() == ".mp3":
            audio = None
            try:
                audio = MP3(self.path, ID3=EasyID3)
            except HeaderNotFoundError:
                LOG.debug("Mutagen not find headers")    
            LOG.debug(EasyID3.valid_keys.keys())
            if audio and audio.has_key('album'): self.album = audio["album"][0]
            if audio and audio.has_key('artist'): self.artist = audio["artist"][0]
            if audio and audio.has_key('title'): self.title = audio["title"][0]
            if audio and audio.has_key('date'): self.date = audio["date"][0]
            if audio and audio.has_key('genre'): self.genre = audio["genre"][0]
            if audio and audio.has_key('tracknumber'): self.tracknumber = audio["tracknumber"][0]

                
