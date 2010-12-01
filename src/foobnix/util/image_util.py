#-*- coding: utf-8 -*-
'''
Created on 11 сент. 2010

@author: ivan
'''
import os
import glob
def get_image_by_path(path):
    dir = os.path.dirname(path)
    if not os.path.isdir(dir):
        return None            
    files = glob.glob(dir + "/*.jpg")
    for file in files:
        for name in ("cover", "face", "front", "case"):                
            if name in file.lower():
                return os.path.join(dir, file)
        """return any"""
    if files:
        return os.path.join(dir, files[0])
    else:
        return None
    
