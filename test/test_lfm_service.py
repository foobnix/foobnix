#-*- coding: utf-8 -*-
'''
Created on 21 нояб. 2010

@author: ivan
'''
import unittest
from foobnix.gui.service.lastfm_service import LastFmService
class TestLastFmService(unittest.TestCase):
    lfm = LastFmService(None)
        
    def test_find_disk_cover(self):
        url = self.lfm.get_album_image_url("Madonna", "Sorry")
        self.assertTrue(url.startswith("http://")) 
    
        
    def test_find_top_tracks(self):
        list = self.lfm.search_top_tracks("Madonna")
        self.assertEquals(50, len(list))        
        for bean in list:
            self.assertTrue(bean.text)
            
        
    
if __name__ == '__main__':
    unittest.main()    
