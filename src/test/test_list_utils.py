#-*- coding: utf-8 -*-
'''
Created on 21 нояб. 2010

@author: ivan
'''
import unittest
from foobnix.util.list_utils import any

class TestListUtils(unittest.TestCase):
        
    def test_any_hof(self):
        isEven = lambda x : x % 2 == 0
        self.assertTrue(any(isEven, [1, 2, 3])) 
        self.assertFalse(any(isEven, [1, 3, 5, 7]))
        self.assertFalse(any(isEven, []))

        isOdd = lambda x : x % 2 == 1
        self.assertTrue(any(isOdd, [1, 2, 3]))
        self.assertFalse(any(isOdd, [2, 4]))        


if __name__ == '__main__':
    unittest.main()    
