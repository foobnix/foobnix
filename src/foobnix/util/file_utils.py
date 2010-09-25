'''
Created on Feb 26, 2010

@author: ivan
'''
import os

def isDirectory(path):
    return os.path.isdir(path)

def get_file_extenstion(fileName):    
    return os.path.splitext(fileName)[1].lower()

def file_extenstion(file_name):    
    return os.path.splitext(file_name)[1].lower()               
