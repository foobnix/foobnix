#-*- coding: utf-8 -*-
'''
Created on 22 нояб. 2010

@author: ivan
'''
import unittest
from foobnix.regui.service.google_service import google_search_results
from foobnix.thirdparty.google.translate import translate
class TestGoogleService(unittest.TestCase):
        
    def test_find_word(self):
        list = google_search_results("Madonna", 10)
        self.assertEquals(10, len(list))
        for line in list:
            self.assertTrue(line is not None)
            
    def test_translate(self):
        result = translate(text="мама", src="ru", to="en")
        self.assertEquals("mom", result)
    
if __name__ == '__main__':
    unittest.main()    
