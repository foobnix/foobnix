#-*- coding: utf-8 -*-
'''
Created on 11 сент. 2010

@author: ivan
'''
import os

from foobnix.util.file_utils import get_file_extension

def get_image_by_path(path):
    
    dir = path if os.path.isdir(path) else os.path.dirname(path)
    
    if not os.path.isdir(dir):
        return None          
    
    ext_list = ['.jpg', '.png', '.bmp', '.tiff', '.gif']
    
    dirs = []
    files = []

    for item in os.listdir(dir):
        if os.path.isdir(os.path.join(dir, item)) and item.lower().startswith("cover"):
            dirs.append(item)
        elif get_file_extension(item) in ext_list:
            files.append(item)
                
    if not files and not dirs:
        return None        
    
    if files:
        for file in files:
            for name in ("cover", "face", "front", "case"):                
                if name in file.lower():
                    return os.path.join(dir, file)
        return os.path.join(dir, files[0])
    
    if dirs:
        for subdir in dirs:
            image = get_image_by_path(os.path.join(dir, subdir))
            if image:
                return image
    
    
    