#-*- coding: utf-8 -*-
'''
Created on 11 сент. 2010

@author: ivan
'''
import os
import glob
from foobnix.util.file_utils import get_file_extension

def get_image_by_path(path):
    dir = os.path.dirname(path)
    if not os.path.isdir(dir):
        return None          
    
    ext_list = ['.jpg', '.png', '.bmp', '.tiff', '.gif']
    
    files = [file for file in os.listdir(dir) if get_file_extension(file) in ext_list]
    
    if not files:
        return None        
    
    for file in files:
        for name in ("cover", "face", "front", "case"):                
            if name in file.lower():
                return os.path.join(dir, file)
    
    return os.path.join(dir, files[0])
    
    
