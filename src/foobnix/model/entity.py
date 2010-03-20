'''
Created on Feb 26, 2010

@author: ivan
'''
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen import File
import os
import gtk
class CommonBean():
    TYPE_FOLDER = "FOLDER"    
    TYPE_MUSIC_FILE = "TYPE_MUSIC_FILE"
    TYPE_MUSIC_URL = "TYPE_MUSIC_URL"
    
    #Song attributes
    album = ""
    artist = ""
    title = ""
    date = ""
    genre = ""
    tracknumber = ""
    
    def __init__(self, name=None, path=None, type=None, is_visible=True, color=None, font="normal", index = -1):
        self.name = name
        self.path = path
        self.type = type
        self.icon = None        
        self.color = color
        self.index = index
        self.time = None
        self.is_visible = is_visible
        self.font = font
        
        #self._getMp3Tags()
    
    def setIconPlaying(self):
        self.icon = gtk.STOCK_GO_FORWARD
    def setIconNone(self):
        self.icon = None
        
    def getTitleDescription(self):    
        if self.title and self.artist and self.album:
            return self.artist + " - [" + self.album + "]  #" + self.tracknumber + " " + self.title
        else:
            return self.name
    
    def getPlayListDescription(self):
        if self.title and self.album:
            return self.title + " (" + self.album + ")"
        return self.name
    
    def _getMp3Tags(self):
        audio = None
        
        if not self.path:
            return
        
        if not self.type:
            return
        
        if self.type != self.TYPE_MUSIC_FILE:
            return
        
        if not os.path.exists(self.path):
            return
        
        try:
            audio = MP3(self.path, ID3=EasyID3)
        except HeaderNotFoundError:
            try:
                audio = File(self.path)
            except HeaderNotFoundError:
                pass        
        
        if audio and audio.has_key('album'): self.album = audio["album"][0]
        if audio and audio.has_key('artist'): self.artist = audio["artist"][0]
        if audio and audio.has_key('title'): self.title = audio["title"][0]
        if audio and audio.has_key('date'): self.date = audio["date"][0]
        if audio and audio.has_key('genre'): self.genre = audio["genre"][0]
        if audio and audio.has_key('tracknumber'): self.tracknumber = audio["tracknumber"][0]
    
    def __str__(self):           
        return "Common Bean :" + self.__contcat(
        "name:", self.name,
        "path:",self.path,
        "type:",self.type,
        "icon:",self.icon,
        "color:",self.color,
        "index:",self.index,
        "time:",self.time,
        "is_visible:",self.is_visible,
        "font:",self.font)
    
    def __contcat(self, *args):
        result = ""
        for arg in args:
            result += " " + str(arg)
        return result   

