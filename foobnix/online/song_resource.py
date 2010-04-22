'''
Created on 20.04.2010

@author: ivan
'''
from foobnix.model.entity import CommonBean

import os
from foobnix.util import LOG
from foobnix.online.vk import Vkontakte
from foobnix.util.configuration import FConfiguration

"""Class to get song resource"""
class SongResource():
    def __init__(self):
        self.vk = Vkontakte(FConfiguration().vk_login, FConfiguration().vk_password)
        if not self.vk.isLive():           
            LOG.error("Vkontakte connection error")

    def get_song_path(self, song):
        if not song.path:
            if song.type == CommonBean.TYPE_MUSIC_URL:                                
                """File exists in file system"""
                if self._check_set_local_path(song):
                    return self.song.path
                
                return self._get_song_remote_url(song)                  
        return None
    
    def _check_set_local_path(self, song):
        file = self._get_cached_song(song)
        if os.path.isfile(file) and os.path.getsize(file) > 1:
            song.path = file
            song.type = CommonBean.TYPE_MUSIC_FILE
            LOG.info("Find file on local disk", song.path)
            return True
        return False
    
    def _get_song_remote_url(self, song):
        LOG.info("Starting search song path in Internet", song.path)                              
        
        """Search by VK"""                
        vkSong = self.vk.find_most_relative_song(song.name)
        if vkSong:                    
            LOG.info("Find song on VK", vkSong, vkSong.path)                      
            return vkSong.path                          
    
    def _make_dirs(self, path):
        if not os.path.isdir(path):
            os.makedirs(path)
    
    
    def _get_cached_song(self, song):
        dir = FConfiguration().onlineMusicPath
        if song.getArtist():
            dir = dir + "/" + song.getArtist()
        self._make_dirs(dir)
        song = dir + "/" + song.name + ".mp3"
        print "Stored dir: ", song
        return song