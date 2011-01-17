'''
Created on Jan 16, 2011

@author: ivan
'''
import unittest
from foobnix.util.list_utils import sort_by_song_name
class Test(unittest.TestCase):

    def test_good_names(self):
        input = ["1.Enigma", "10.Bee", "11.Some", "2.KOT"]
        result = ["1.Enigma", "2.KOT", "10.Bee", "11.Some"]
        self.assertEquals(result, sort_by_song_name(input))
        
    def test_bad_name(self):
        input = ["a1.Enigma", "a10.Bee", "a11.Some", "a2.KOT"]
        result = ["a1.Enigma", "a10.Bee", "a11.Some", "a2.KOT"]
        self.assertEquals(result, sort_by_song_name(input))
        
    def test_bad_name_alpha(self):
        input = ["aEnigma", "cBee", "bSome", "dKOT"]
        result = ["aEnigma", "bSome", "cBee", "dKOT"]
        self.assertEquals(result, sort_by_song_name(input))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
