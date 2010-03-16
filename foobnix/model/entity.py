'''
Created on Feb 26, 2010

@author: ivan
'''
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3, HeaderNotFoundError
from mutagen import File
import os
class EntityBean():
    TYPE_FOLDER = "FOLDER"
    TYPE_MUSIC_FILE = "TYPE_MUSIC_FILE"
    TYPE_MUSIC_URL = "TYPE_MUSIC_URL"
    
    def __init__(self, name=None, path=None, type=None):
        self.name = name
        self.path = path
        self.type = type
    
    def init(self, entity):
        self.name = entity.name
        self.path = entity.path
        self.type = entity.type
        return self       

class URLBeen(EntityBean):
        def __init__(self, name=None, path=None, type = EntityBean.TYPE_MUSIC_URL):
            EntityBean.__init__(self, name, path, type)
               
        
class SongBean(EntityBean):
    album = ""
    artist = ""
    title = ""
    date = ""
    genre = ""
    tracknumber = ""           
    def __init__(self, name=None, path=None, type = EntityBean.TYPE_MUSIC_FILE):                       
        EntityBean.__init__(self, name, path, type)        
        
        self._getMp3Tags()
        

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
        

class PlaylistBean(SongBean):
    def __init__(self, icon=None,tracknumber="", name=None, path=None, color=None, index =0, type=None):
        SongBean.__init__(self, name, path)
        self.icon = icon        
        self.color = color 
        self.tracknumber = tracknumber
        self.index = index
        self.type = type
        
class DirectoryBean(EntityBean):    
    def __init__(self, name, path, font=10, is_visible=True, type=EntityBean.TYPE_FOLDER):
        EntityBean.__init__(self, name, path, type)        
        self.font = font
        self.is_visible = is_visible      
