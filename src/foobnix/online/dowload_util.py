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
from mutagen.id3 import ID3NoHeaderError, ID3, TIT2, COMM, TPE1, TENC, TDRC, \
    TALB

def dowload_song_thread(song):
    thread.start_new_thread(download_song, (song,))
    
def save_song_thread(songs):
    thread.start_new_thread(save_song, (songs,))
    #save_song(songs)

def save_as_song_thread(songs, path):
    LOG.debug("Begin download songs list", songs)
    thread.start_new_thread(save_as_song, (songs, path,))
    

def save_song(songs):
    for song in songs:    
        update_song_path(song)
        file = get_file_store_path(song)
        LOG.debug("Download song start", file)
        if not os.path.exists(file + ".tmp") and song.path:
            LOG.debug("Song PATH", song.path)
            urllib.urlretrieve(song.path, file + ".tmp")
            os.rename(file + ".tmp", file)
            update_id3_tags(song, file)
            LOG.debug("Download song finished", file)
        else:
            LOG.debug("Found file already dowloaded", file)


def save_as_song(songs, path):
    for song in songs:
        update_song_path(song)
        
        if song.name.endswith(".mp3"):
            file = path + "/" + song.name
        else:
            file = path + "/" + song.name + ".mp3"
            
        LOG.debug("Download song start", file)
        if not os.path.exists(file + ".tmp") and song.path:
            urllib.urlretrieve(song.path, file + ".tmp")
            os.rename(file + ".tmp", file)
            update_id3_tags(song, file)
            LOG.debug("Download song finished", file)
        else:
            LOG.debug("Found file already dowloaded", file)

def update_id3_tags(song, path):
    if os.path.exists(str(path)):
        LOG.debug("Begin update", path)
        #audio = EasyID3(str(path))
        try: 
            tags = ID3(path)
        except ID3NoHeaderError:
            LOG.info("Adding ID3 header;")
            tags = ID3()
   
        tags["TIT2"] = TIT2(encoding=3, text=song.getTitle())
        tags["COMM"] = COMM(encoding=3, lang="eng", desc='desc', text='Grab by www.foobnix.com')
        tags["TENC"] = TENC(encoding=3, text='www.foobnix.com')
        tags["TPE1"] = TPE1(encoding=3, text=song.getArtist())
        
        tags["TDRC"] = TDRC(encoding=3, text=song.year)
        tags["TALB"] = TALB(encoding=3, text=song.album)
        
        try:
            tags.save(path)
        except:
            LOG.error("Tags can't be updated")
            pass
       
        LOG.debug("ID3 TAGS updated")
    else:
        LOG.error("ID3 FILE not found", path)
    

"""Dowload song proccess"""
def download_song(song):
    if not FConfiguration().is_save_online:
        LOG.debug("Saving (Caching) not enable")
        return None    
    save_song([song])
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
            
