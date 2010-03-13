'''
Created on Feb 26, 2010

@author: ivan
'''
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
        
class SongBean(EntityBean):           
    def __init__(self, name=None, path=None, type = EntityBean.TYPE_MUSIC_FILE):                       
        EntityBean.__init__(self, name, path, type)
        self.tracknumber = None

class PlaylistBean(SongBean):
    def __init__(self, icon=None,tracknumber=10, name=None, path=None, color=None, index =0):
        SongBean.__init__(self, name, path)
        self.icon = icon        
        self.color = color 
        self.tracknumber = tracknumber
        self.index = index
        
class DirectoryBean(EntityBean):    
    def __init__(self, name, path, font=10, is_visible=True, type=EntityBean.TYPE_FOLDER):
        EntityBean.__init__(self, name, path, type)        
        self.font = font
        self.is_visible = is_visible      
