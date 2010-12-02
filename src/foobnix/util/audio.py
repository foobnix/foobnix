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
from foobnix.util import LOG

def get_mutagen_audio (path):
    LOG.debug("GET mutagen audio", path)
    ext = get_file_extenstion(path)
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
    return audio
