'''
Created on Jun 10, 2010

@author: ivan
'''
from foobnix.util.configuration import FConfiguration
from foobnix.util import LOG
import os
import urllib
import thread
from foobnix.online.song_resource import update_song_path
from mutagen.easyid3 import EasyID3

def dowload_song_thread(song):
    thread.start_new_thread(download_song, (song,))
    
def save_song_thread(songs):
    thread.start_new_thread(save_song, (songs,))

def save_as_song_thread(songs, path):
    LOG.debug("Begin download songs list", songs)
    thread.start_new_thread(save_as_song, (songs,path,))
    

def save_song(songs):
    for song in songs:    
        update_song_path(song)
        file = get_file_store_path(song)
        LOG.debug("Download song start", file)
        if not os.path.exists(file + ".tmp"):
            LOG.debug("Song PATH", song.path)
            urllib.urlretrieve(song.path, file + ".tmp")
            os.rename(file + ".tmp", file)
            LOG.debug("Download song finished", file)
        else:
            LOG.debug("Found file already dowloaded", file)


def save_as_song(songs, path):
    for song in songs:
        update_song_path(song)
        file = path +  "/" + song.name + ".mp3"
        LOG.debug("Download song start", file)
        if not os.path.exists(file + ".tmp"):
            urllib.urlretrieve(song.path, file + ".tmp")
            os.rename(file + ".tmp", file) 
            LOG.debug("Download song finished", file)
        else:
            LOG.debug("Found file already dowloaded", file)

def update_id3_tags(song, path):
    audio = EasyID3(path)
    audio["title"] = song.getArtist()
    audio["artist"] = song.getTitle()
    audio["album"] = song.album
    audio["date"] = song.year
    audio.save()
    
    

"""Dowload song proccess"""
def download_song(song):
    if not FConfiguration().is_save_online:
        LOG.debug("Saving (Caching) not enable")
        return None    
    save_song(song)
    pass

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
            