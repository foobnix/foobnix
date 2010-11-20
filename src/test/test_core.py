#-*- coding: utf-8 -*-
'''
Created on 20 нояб. 2010

@author: ivan
'''
import unittest
from foobnix.regui.foobnix_core import FoobnixCore
from foobnix.regui.about.about import AboutWindow
class TestFoobnixCore(unittest.TestCase):
    def test_main_window(self):
        w = FoobnixCore(DEBUG=True)
        w = None        
        self.assertTrue(True)
        
             
    
    def test_about_window(self):
        w = AboutWindow()
        w.destroy()
        self.assertTrue(True)
    
        
if __name__ == '__main__':
    unittest.main()
