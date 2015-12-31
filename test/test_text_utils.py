#-*- coding: utf-8 -*-
import unittest
from foobnix.util.text_utils import smart_splitter, capitalize_string, \
    capitalize_query, split_string, normalize_text

class TestCapitalizeFunctions(unittest.TestCase):
    def test_capitalize_None(self):
        self.assertEquals(None, capitalize_string(None))
        self.assertEquals("", capitalize_string(""))
        
    def test_capitalize(self):
        self.assertEquals(u"Madonna Music", capitalize_string("MaDoNna MUSIC"))
        self.assertEquals(u"Madonna", capitalize_string("MaDoNna"))

class TestCapitalizeQueryFunctions(unittest.TestCase):
    def test_capitalize_None(self):
        self.assertEquals(None, capitalize_query(None))
        self.assertEquals("", capitalize_query(""))
        
    def test_capitalize_url(self):
        self.assertEquals(u"http://Madonna", capitalize_query("http://Madonna"))
    
    def test_capitalize_string(self):
        self.assertEquals(u"Ddt", capitalize_query("ddt"))
        self.assertEquals(u"DDT", capitalize_query("DDT"))
        self.assertEquals(u"DDT Music", capitalize_query("DDT music"))


class TestSplitterFunctions(unittest.TestCase):
    def setUp(self):
        self.input = "abcde 1234 w2e3"
    
    def test_empty_string(self):
        result = smart_splitter(None, 3)
        self.assertEquals(None, result)
        
    def test_empty_len(self):
        result = smart_splitter("100", None)
        self.assertEquals(["100"], result)
        
    def test_good_splitter(self):
        result = smart_splitter(self.input, 4)
        self.assertEquals(["abcde", "1234", "w2e3"], result)
    
    def test_good_splitter1(self):
        result = smart_splitter(self.input, 2)
        self.assertEquals(["abcde", "1234", "w2"], result)


class TestSplitStringFunction(unittest.TestCase):
    def setUp(self):
        self.input = "abcde,1234 w2    e3fdfd"
    
    def test_empty_string(self):
        result = split_string("", 3)
        self.assertEquals("", result)
        
    def test_empty_len(self):
        result = split_string("100", 3)
        self.assertEquals("100\n", result)
        
    def test_good_splitter(self):
        result = split_string(self.input, 10)
        self.assertEquals("abcde,\n1234 w2\ne3fdfd", result)
    
    def test_good_splitter1(self):
        result = split_string(self.input, 19)
        self.assertEquals("abcde,1234 w2\ne3fdfd", result)

class TestNormalizeFunctions(unittest.TestCase):
    def test_normalize_function(self):
        self.assertEquals(u"Madonna - Music", normalize_text("01 - Madonna - Music.mp3"))
        self.assertEquals(u"Madonna", normalize_text("Madonna.mp3"))
        self.assertEquals(u"Madonna", normalize_text("01 - Madonna [music].MP3"))
        self.assertEquals(u"Madonna - Music", normalize_text("01-Madonna - MUSIC.ogg"))
        self.assertEquals(u"Enigma - Sadeness Part", normalize_text("1.ENIGMA - SADENESS PART.mp3"))
        self.assertEquals(u"Similar Tracks - Give A Little More", normalize_text("Similar Tracks - Give A Little More *** www.ipmusic.ch ***"))
        self.assertEquals(u"Similar Feat. Tracks - Give A Little More", normalize_text("Similar feat. Tracks  - Give A Little More *** www.ipmusic.ch ***"))
        
        

if __name__ == '__main__':
    unittest.main()

