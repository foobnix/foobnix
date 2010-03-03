'''
Created on Mar 2, 2010

@author: ivan
'''
from unittest import TestCase
from dirlist import DirectoryList
import os
from confguration import FConfiguration

class TestSomeFunctional(TestCase):
    def setUp(self):
        self.a = 5
        
    def taerDown(self):
        print "tear down"
        
    def testSomeFunctional(self):
        self.assertEquals(10, self.a + 5)
    
    
    def isDirectory(self, path):
        return os.path.isdir(path)
    
    def getExtenstion(self, fileName):
        return fileName[-4:].lower()
        
    def isDirectoryWithMusic1(self, path):
        if self.isDirectory(path):
            print "path is a dir ", path
            dir = os.path.abspath(path)
            list = os.listdir(dir)
            for file in list:
                full_path = path + "/" + file
                if self.isDirectory(full_path):
                    print "sub dir", full_path                                    
                    if self.isDirectoryWithMusic(full_path):
                        return True
                else:
                    print "sub file", full_path
                    if self.getExtenstion(file) in FConfiguration().supportTypes:
                        return True
                    else:
                        print "FILE IS NOT FOUND!!!!!"                        
        else:
            print "File name" + path
                    
        return False  
    
     
    def isDirectoryWithMusic(self, path):
        if self.isDirectory(path):
            dir = os.path.abspath(path)
            list = os.listdir(dir)
            for file in list:
                full_path = path + "/" + file
                if self.isDirectory(full_path):                                    
                    if self.isDirectoryWithMusic(full_path):
                        return True                    
                else:
                    if self.getExtenstion(file) in FConfiguration().supportTypes:
                        return True
                    
        return False            
        
        
            
    def test_isDirectoryWithMusic(self):        
        self.assertTrue(self.isDirectoryWithMusic("/home/ivan/Music/Cranberries"))
        self.assertTrue(self.isDirectoryWithMusic("/home/ivan/Music/Depeche Mode Official Discography - FLAC (tracks)"))
        self.assertFalse(self.isDirectoryWithMusic("/home/ivan/Music/English"))
        self.assertFalse(self.isDirectoryWithMusic("/home/ivan/Music/2009 - Sing-Along Songs For The Damned And Delirious [ASC23013CDSP]/Covers"))
        
