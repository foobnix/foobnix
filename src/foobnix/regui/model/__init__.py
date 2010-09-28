import gobject

class FTreeModel():   
    
    def __init__(self):
        self.text = 0, str
        self.visible = 1, gobject.TYPE_BOOLEAN
        self.font = 2, str
        self.play_icon = 3, str
        self.time = 4, str
        self.path = 5, str
        self.level = 6, str
        self.tracknumber = 7, str
        self.index = 8, int
        self.is_file = 9, gobject.TYPE_BOOLEAN
        
        self.artist = 10, str
        self.title = 11, str
        self.image = 12, str
        self.album = 13, str
        self.genre = 14, str
    
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
    
    def add_artist(self, artist):
        self.artist = artist
        return self
    
    def add_title(self, title):
        self.title = title
        return self
        
    def add_level(self, level):
        self.level = level
        return self 
    
    def add_font(self, font):
        self.font = font
        return self
    
    def add_is_file(self, is_file):
        self.is_file = is_file
        return self
    def add_album(self, album):
        self.album = album
        return self
    
    def add_play_icon(self, play_icon):
        self.play_icon = play_icon
        return self  
    
    def add_genre(self, genre):
        self.genre = genre
        return self   
    
    def __str__(self):
        return "FModel: " + str(self.__dict__)
