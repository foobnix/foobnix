'''
Created on Nov 10, 2010

@author: ivan
'''
from foobnix.util.file_utils import get_file_extension
from mutagen.monkeysaudio import MonkeysAudio
from mutagen.mp3 import MP3
from mutagen.wavpack import WavPack
from mutagen.ogg import OggFileType
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
import logging
from mutagen.flac import FLAC

def get_mutagen_audio (path):
    logging.debug("GET mutagen audio" + path)
    ext = get_file_extension(path)
    audio = None
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
    if ext == ".m4a" or ext == ".mp4":
        audio = MP4(path)
        
    return audio
