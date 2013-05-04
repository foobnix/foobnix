'''
Created on Nov 10, 2010

@author: ivan
'''

import logging

from foobnix.thirdparty.mutagen.asf import ASF
from foobnix.thirdparty.mutagen.mp3 import MP3
from foobnix.thirdparty.mutagen.mp4 import MP4
from foobnix.thirdparty.mutagen.flac import FLAC
from foobnix.thirdparty.mutagen.easyid3 import EasyID3
from foobnix.thirdparty.mutagen.wavpack import WavPack
from foobnix.thirdparty.mutagen.oggvorbis import OggVorbis
from foobnix.thirdparty.mutagen.monkeysaudio import MonkeysAudio

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
            from foobnix.thirdparty.mutagen.oggtheora import OggTheora
            try:
                audio = OggTheora(path)
            except:
                from foobnix.thirdparty.mutagen.oggflac import OggFLAC
                try:
                    audio = OggFLAC(path)
                except:
                    from foobnix.thirdparty.mutagen.oggspeex import OggSpeex
                    try:
                        audio = OggSpeex(path)
                    except:
                        logging.error("This file in not ogg format")
                                    
    if ext == ".m4a" or ext == ".mp4" or ext == ".mkv":
        audio = MP4(path)
        
    return audio 
