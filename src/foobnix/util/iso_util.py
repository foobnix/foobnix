#-*- coding: utf-8 -*-
'''
Created on 1 дек. 2010

@author: ivan
'''
import subprocess
import os
def mount_tmp_iso(path):
    print  path
    if not os.path.isdir("/tmp/demo"):
        os.mkdir("/tmp/demo")
    command = ["mount", "-o", "loop", path, "/tmp/demo"]
    print command
    retcode = subprocess.call(["mount", "-o", "loop", path, "/tmp/demo"])
    print retcode


mount_tmp_iso("/home/ivan/Музыка/Joni.Mitchell-2004.The.Beginning.of.Survival.(Compilation.Album).(Geffen.B0002836-02).by.yury_usa.NL+0802.iso.wv")
