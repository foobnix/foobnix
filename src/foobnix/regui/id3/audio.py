'''
Created on Nov 10, 2010

@author: ivan
'''
from foobnix.util.file_utils import get_file_extenstion
from mutagen.flac import FLAC
from mutagen.monkeysaudio import MonkeysAudio
from mutagen.mp3 import MP3
from mutagen.wavpack import WavPack
from mutagen.ogg import OggFileType
from mutagen.easyid3 import EasyID3
import re
def get_mutagen_audio (path):
    ext = get_file_extenstion(path)
    if ext == ".flac":
        audio = FLAC(path)
    if ext == ".ape":
        audio = MonkeysAudio(path)
    if ext == ".mp3":
        audio = MP3(path, ID3=EasyID3)
    if ext == ".wv":
        audio = WavPack(path)
    if ext == ".ogg":
        audio = OggFileType(path)
    return audio

def normilize_text(line):
    """find in extension"""
    dot_index = line.rfind(".")
    if dot_index >= 0:
        line = line[:dot_index]
        
    dot_index = line.rfind("(")
    if dot_index >= 0:
        line = line[:dot_index]
    
    dot_index = line.find("*")
    if dot_index >= 0:
        line = line[:dot_index]
    
    """find in prefix"""
    prefix_index = re.search('^([ 0-9.-]*)', line).end()   
    line = line[prefix_index:]
    
    return line.strip()
