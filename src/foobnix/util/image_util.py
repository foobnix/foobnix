#-*- coding: utf-8 -*-
'''
Created on 11 сент. 2010

@author: ivan
'''
import os
def get_image_by_path(path):
    dir = os.path.dirname(path)
    files = os.listdir(dir)
    for file in files:
        if file.lower().endswith(".jpg"):
            original = file
            file = file.lower()
            if file.find("cover") >= 0:
                return os.path.join(dir, original)
            if file.find("face") >= 0:
                return os.path.join(dir, original)
            if file.find("front") >= 0:
                return os.path.join(dir, original)
            if file.find("case") >= 0:
                return os.path.join(dir, original)
            """return any"""
            return os.path.join(dir, original)
    return None
