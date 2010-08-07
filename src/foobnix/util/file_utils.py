'''
Created on Feb 26, 2010

@author: ivan
'''
import os

def isDirectory(path):
    return os.path.isdir(path)

def get_file_extenstion(fileName):    
    return os.path.splitext(fileName)[1].lower()
               
