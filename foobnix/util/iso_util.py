#-*- coding: utf-8 -*-
'''
Created on 1 дек. 2010

@author: ivan
'''

import os
import logging
import subprocess

from foobnix.gui.service.music_service import get_all_music_with_id3_by_path

def get_beans_from_iso_wv(path):
    if path and path.lower().endswith("iso.wv"):
        mount_path = mount_tmp_iso(path)        
        beans = get_all_music_with_id3_by_path(mount_path, True)
        for bean in beans:
            bean.add_iso_path(path)
        return beans
    
      
def mount_tmp_iso(path):
    name = os.path.basename(path)
    tmp_dir = os.path.join("/tmp", name)
    if os.path.exists(tmp_dir):
        logging.debug("tmp dir to mount already exists" + tmp_dir)
        return tmp_dir
    command = ["fuseiso", "-n", "-p", path, tmp_dir]
    logging.debug("Mount iso.wv %s" % command)
    subprocess.call(command)
    return tmp_dir
