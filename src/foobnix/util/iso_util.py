#-*- coding: utf-8 -*-
'''
Created on 1 дек. 2010

@author: ivan
'''
import subprocess
import os
import logging
from foobnix.regui.service.music_service import get_all_music_by_paths

def get_beans_from_iso_wv(path):
    if path and path.lower().endswith("iso.wv"):
        mount_path = mount_tmp_iso(path)        
        return get_all_music_by_paths([mount_path])  

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
