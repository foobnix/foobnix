'''
Created on Feb 26, 2010

@author: ivan
'''
import os

def isDirectory(path):
    return os.path.isdir(path)

def getExtenstion(fileName):
    return fileName[-4:].lower()
               
