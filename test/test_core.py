#-*- coding: utf-8 -*-
'''
Created on 20 нояб. 2010

@author: ivan
'''
import unittest
from foobnix.regui.foobnix_core import FoobnixCore
class TestFoobnixCore(unittest.TestCase):    
    def __test_main_window(self):
        self.w = FoobnixCore()
        self.assertTrue(True)
        self.w = None
    
    def test_veraion(self):
        self.assertTrue('0.2.2-10ppa0' > '0.2.2-09ppa0')
        self.assertTrue('0.2.2-9ppa0' > '0.2.2-09ppa0')
        
if __name__ == '__main__':
    unittest.main()
