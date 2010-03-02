'''
Created on Mar 2, 2010

@author: ivan
'''
from unittest import TestCase
import __main__
import unittest

class TestSomeFunctional(TestCase):
    def setUp(self):
        self.a = 5
        
    def taerDown(self):
        print "tear down"
        
    def testSomeFunctional(self):
        self.assertEquals(10, self.a + 5)

