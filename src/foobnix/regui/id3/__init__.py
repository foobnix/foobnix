from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
class ID3Model():
    def __init__(self):
        self.text = None        
        self.artist = None
        self.title = None
        self.info = None

def get_id3(path):
    path = path.lower()
    id3model = ID3Model()
    audio = None 
    if path.endswith(".mp3"):
        audio = MP3(path, ID3=EasyID3)
    
    if audio and audio.has_key('artist'): id3model.artist = audio["artist"][0]
    if audio and audio.has_key('title'): id3model.title = audio["title"][0]
    if audio.info: id3model.info = audio.info.pprint()
    return id3model

    

 
