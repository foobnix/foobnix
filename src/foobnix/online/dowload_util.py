'''
Created on Jun 10, 2010

@author: ivan
'''
from foobnix.util.configuration import FConfiguration
from foobnix.util import LOG
import os
import urllib
import thread


def dowload_song_thread(song):
    thread.start_new_thread(download_song, (song,))        

"""Dowload song proccess"""
def download_song(song):
    if not FConfiguration().is_save_online:
        LOG.debug("Saving (Caching) not enable")
        return None
    LOG.debug("Download song start", song)
    file = get_file_store_path(song)
    if not os.path.exists(file + ".tmp"):
        r = urllib.urlretrieve(song.path, file + ".tmp")
        os.rename(file + ".tmp", file)        
        LOG.debug("Download song finished", file)
    else:
        LOG.debug("Found file already dowloaded", file)

"""Determine file place"""
def get_file_store_path(song):
        dir = FConfiguration().onlineMusicPath
        if song.getArtist():
            dir = dir + "/" + song.getArtist()
        make_dirs(dir)
        song = dir + "/" + song.name + ".mp3"
        return song
    
def make_dirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)
            