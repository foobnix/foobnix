#-*- coding: utf-8 -*-
'''
Created on 21 нояб. 2010

@author: ivan
'''
import unittest
from foobnix.regui.service.vk_service import VKService
import urllib
from foobnix.util.url_utils import get_url_type
class TestVkService(unittest.TestCase):
    vk = VKService()
        
    def test_find_videos(self):
        list = self.vk.find_video_by_query("Мадонна")
        for bean in list:
            print bean.path
            self.assertTrue(bean.path.startswith("http://")) 
    
    def test_find_track(self):
        bean = self.vk.find_one_track("Мадонна")        
        self.assertTrue(bean.path.startswith("http://"))
    
    def test_bad_link_track(self):
        beans = self.vk.find_video_by_query("akon-cry out of jou(michael jackson tribute")
        "http://cs12907.vkontakte.ru/u87507380/video/bee60bc871.240.mp4"
        path = beans[0].path
        self.assertNotEquals("text/html", get_url_type(path))
        
                    
    def test_find_by_url(self):
        list = self.vk.find_tracks_by_url("http://vkontakte.ru/audio.php?gid=2849#album_id=0&gid=2849&id=0&offset=200")        
        for bean in list:
            self.assertTrue(bean.path.startswith("http://"))
   
    
if __name__ == '__main__':
    unittest.main()        
        
