# -*- coding: utf-8 -*-
'''
Created on Feb 27, 2010

@author: ivan
'''
import os
import random
FOOBNIX_TMP = "/usr/share/foobnix"
FOOBNIX_TMP_RADIO = os.path.join(FOOBNIX_TMP, "radio")
FOOBNIX_VERSION_FILE_NAME = "version"

USER_DIR = os.getenv("HOME") or os.getenv('USERPROFILE')
CFG_FILE_DIR = os.path.join(USER_DIR, ".config/foobnix")
CFG_FILE = os.path.join(CFG_FILE_DIR, "foobnix_conf.pkl")

"""get last version from file"""
def get_version():
    result = "A"
    version_file = None
    if os.path.exists(os.path.join(FOOBNIX_TMP, FOOBNIX_VERSION_FILE_NAME)):
        version_file = os.path.join(FOOBNIX_TMP, FOOBNIX_VERSION_FILE_NAME)
    elif os.path.exists(FOOBNIX_VERSION_FILE_NAME):
        version_file = os.path.join(FOOBNIX_VERSION_FILE_NAME)

    with file(version_file, 'r') as v_file:

        for line in v_file:
            line = str(line).strip()
            if line.find("VERSION=") >= 0:
                result = line[len("VERSION="):]
            elif line.find("RELEASE=") >= 0:
                result += "-" + line[len("RELEASE="):]
    return result

VERSION = get_version()

def check_create_cfg_dir():
    if not os.path.exists(CFG_FILE_DIR):
        os.makedirs(CFG_FILE_DIR)

def get_random_vk():
    vks = {
       "c891888@bofthew.com":"c891888",
       "c892009@bofthew.com":"c892009",
       "c892406@bofthew.com":"c892406",
       "c892588@bofthew.com":"c892588"       
       }

    rand = random.randint(0,len(vks)-1)
    key = vks.keys()[rand]
    value =  vks[key]
    return key, value