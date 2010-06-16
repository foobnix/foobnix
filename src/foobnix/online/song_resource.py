'''
Created on 20.04.2010

@author: ivan
'''
from foobnix.model.entity import CommonBean

import os
from foobnix.util import LOG
from foobnix.online.vk import Vkontakte
from foobnix.util.configuration import FConfiguration

try:
    vk = Vkontakte(FConfiguration().vk_login, FConfiguration().vk_password)
except:
    vk = None
    LOG.error("Vkontakte connection error")

def get_song_path(song):
    if not song.path:
        if song.type == CommonBean.TYPE_MUSIC_URL:                                
            """File exists in file system"""
            if _check_set_local_path(song):
                return song.path
            
            return _get_song_remote_url(song)                  
    return None

def get_songs_by_url(url):
    return vk.get_songs_by_url(url);

def find_song_urls(title):
    return vk.find_song_urls(title)

def update_song_path(song):
    if not song.path:
        if song.type == CommonBean.TYPE_MUSIC_URL:                                
            """File exists in file system"""
            if _check_set_local_path(song):
                return song.path
            
            song.path = _get_song_remote_url(song)                  
    

def _check_set_local_path(song):
    file = _get_cached_song(song)
    if os.path.isfile(file) and os.path.getsize(file) > 1:
        song.path = file
        song.type = CommonBean.TYPE_MUSIC_FILE
        LOG.info("Find file on local disk", song.path)
        return True
    return False

def _get_song_remote_url(song):
    LOG.info("Starting search song path in Internet", song.path)                              
    
    """Search by VK"""                
    vkSong = vk.find_most_relative_song(song.name)
    if vkSong:                    
        LOG.info("Find song on VK", vkSong, vkSong.path)                      
        return vkSong.path                          

def _make_dirs(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def _get_cached_song(song):
    dir = FConfiguration().onlineMusicPath
    if song.getArtist():
        dir = dir + "/" + song.getArtist()
    _make_dirs(dir)
    song = dir + "/" + song.name + ".mp3"
    print "Stored dir: ", song
    return song
