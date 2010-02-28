'''
Created on Feb 26, 2010

@author: ivan
'''
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3

import os
class Song:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        
        self.album = None
        self.artist = None
        self.title = None
        self.date = None
        self.genre = None
        self.tracknumber = None
        if os.path.isfile(self.path):
            self._getMp3Tags()
    
    def getFullDescription(self):
        return self.artist + " - ["+self.album + "]  #"+self.tracknumber + " " + self.title
    
    def getShorDescription(self):
        return self.tracknumber +" " +  self.title + " (" + self.album + ")"
                            
               
    def _getMp3Tags(self):
        audio = MP3(self.path, ID3=EasyID3)
        self.album = audio["album"][0]
        self.artist = audio["artist"][0]
        self.title = audio["title"][0]
        self.date = audio["date"][0]
        self.genre = audio["genre"][0]
        self.tracknumber = audio["tracknumber"][0]
        return self
