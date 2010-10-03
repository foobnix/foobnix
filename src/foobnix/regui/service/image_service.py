#-*- coding: utf-8 -*-
'''
Created on 3 окт. 2010

@author: ivan
'''
import os
def get_foobnix_pixmap_path_by_name(name):    
        icon_path = os.path.join("/usr/local/share/pixmaps", name)
        icon_path2 = os.path.join("/usr/share/pixmaps", name)
        local_path = os.path.join("pixmaps", name)
        
        if os.path.exists(local_path):
            return local_path
        elif os.path.exists(icon_path):
            return icon_path
        elif os.path.exists(icon_path2):
            return icon_path2        
        return None
