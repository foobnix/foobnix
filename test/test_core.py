#-*- coding: utf-8 -*-
'''
Created on 20 нояб. 2010

@author: ivan
'''
import unittest
from foobnix.regui.foobnix_core import FoobnixCore
class TestFoobnixCore(unittest.TestCase):
    def test_main_window(self):
        FoobnixCore()
        self.assertTrue(True)        
        
if __name__ == '__main__':
    unittest.main()
