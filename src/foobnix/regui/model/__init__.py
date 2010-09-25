from foobnix.regui.treeview import FModel
"""common system bean"""

class FBean(FModel):
    TYPE_SONG = "SONG"
    TYPE_FOLDER = "FOLDER"
    
    def __init__(self, text=None, path=None):
        FModel.__init__(self, True)
        self.text = text        
        self.path = path
    
    def add_level(self, level):
        self.level = level
        return self 
    
    def add_font(self, font):
        self.font = font
        return self
    
    def add_is_file(self, is_file):
        self.is_file = is_file
        return self
    
    def add_play_icon(self, play_icon):
        self.play_icon = play_icon
        return self
