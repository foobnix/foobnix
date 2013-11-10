'''
Created on Nov 10, 2010

@author: ivan
'''

import logging

from mutagen.asf import ASF
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.wavpack import WavPack
from mutagen.oggvorbis import OggVorbis
from mutagen.monkeysaudio import MonkeysAudio

from foobnix.util.file_utils import get_file_extension


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
    if ext == ".wma":
        audio = ASF(path)
    if ext == ".ogg":
        try:
            audio = OggVorbis(path)
        except:
            from mutagen.oggtheora import OggTheora
            try:
                audio = OggTheora(path)
            except:
                from mutagen.oggflac import OggFLAC
                try:
                    audio = OggFLAC(path)
                except:
                    from mutagen.oggspeex import OggSpeex
                    try:
                        audio = OggSpeex(path)
                    except:
                        logging.error("This file in not ogg format")
                                    
    if ext == ".m4a" or ext == ".mp4" or ext == ".mkv":
        audio = MP4(path)
        
    return audio 
