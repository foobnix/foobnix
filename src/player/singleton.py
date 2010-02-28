'''
Created on Feb 28, 2010

@author: ivan
'''
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import mutagen.id3
from song import Song

def test():
    """Example which shows how to automatically add tags to an MP3 using EasyID3."""

    audio = MP3("/home/ivan/Music/CD1/01 Another Brick In The Wall.mp3", ID3=EasyID3)
    #print audio
    #print audio.pprint()
    
    s = Song("AAA", "/home/ivan/Music/CD1/01 Another Brick In The Wall.mp3")
    print s.getFullDescription()

test()
