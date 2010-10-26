import gobject
import uuid

class FTreeModel():   
   
    def __init__(self):
        
        self.text = 0 , str        
        self.visible = 1 , gobject.TYPE_BOOLEAN        
        self.font = 2 , str
        self.play_icon = 3 , str
        self.time = 4 , str
        self.path = 5 , str
        self.level = 6 , str
        self.tracknumber = 7 , str        
        self.is_file = 8 , gobject.TYPE_BOOLEAN
        
        self.artist = 9 , str
        self.title = 10 , str
        self.image = 11 , str
        self.album = 12 , str
        self.genre = 13 , str
        self.year = 14 , str
        self.info = 15 , str
        
        self.start_sec = 16 , str
        self.duration_sec = 17 , str
        
        self.UUID = 18 , str
        self.parent_level = 19 , str
        self.type = 20 , str
    
    def cut(self):
    
        for i in self.__dict__:
            self.__dict__[i] = self.__dict__[i][0]
        return self
    
    def types(self):
        types = []
        for i in xrange(0, len(self.__dict__)):
            for j in self.__dict__:
                id = self.__dict__[j][0]
                type = self.__dict__[j][1]
                if i == id:
                    types.append(type) 
                    break;
        return types
        
class FModel(FTreeModel):             
    TYPE_SONG = "SONG"
    TYPE_FOLDER = "FOLDER"
    
    def __init__(self, text=None, path=None):
        FTreeModel.__init__(self)
        for i in self.__dict__:
            self.__dict__[i] = None
        self.text = text
        self.path = path
        self.visible = True
        self.UUID = uuid.uuid4().hex
        self.level = uuid.uuid4().hex
        
    def create_from_text(self, text):
        self.text = text
        if " - " in text:
            list = text.split(" - ")
            self.add_artist(list[0].strip()).add_title(list[1].strip())
        return self
    
    def get_display_name(self):
        if self.artist and self.title:
            return self.artist + " - " + self.title
        else:
            return self.text
     
    def get_uuid(self):
        return self.UUID
    
    def add_type(self, type):
        self.type = type
        return self
    
    def add_artist(self, artist):
        self.artist = artist
        return self
    
    def add_title(self, title):
        self.title = title
        return self
        
    def add_level(self, level):
        self.level = level
        return self
    
    def get_level(self):
        return self.level
    
    def add_parent(self, parent):
        self.parent_level = parent
        return self 
    
    def parent(self, parent_bean):
        self.parent_level = parent_bean.level
        self.is_file = True
        return self
    def set_parent(self, parent):
        self.parent_level = parent
    
    def get_parent(self):
        return self.parent_level
    
    def add_font(self, font):
        self.font = font
        return self
    
    def add_is_file(self, is_file):
        self.is_file = is_file
        return self
    
    def add_album(self, album):
        self.album = album
        return self
    
    def add_year(self, year):
        self.year = year
        return self
    
    def add_play_icon(self, play_icon):
        self.play_icon = play_icon
        return self  
    
    def add_genre(self, genre):
        self.genre = genre
        return self   
    
    def add_time(self, time):
        self.time = time
        return self
    
    def __str__(self):
        return "FModel: " + str(self.__dict__)