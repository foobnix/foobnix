#-*- coding: utf-8 -*-
import os.path

def m3u_reader(m3u_file_path):
    lines = open(unicode(m3u_file_path)).readlines()
    paths = [os.path.normpath(line) for line in lines if not line.startswith("#")]
    dirname = os.path.dirname(m3u_file_path)
    full_paths = [os.path.join(dirname, path).replace("\\", "/").strip('\r\n') for path in paths]
    return full_paths