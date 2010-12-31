#-*- coding: utf-8 -*-
import os.path

def m3u_reader(m3u_file_path):
    lines = open(unicode(m3u_file_path)).readlines()
    paths = [os.path.normpath(line) for line in lines if not line.startswith("#")]
    dirname = os.path.dirname(m3u_file_path)
    if paths[0][0] == "\\" or paths[0][0] == '/':
        full_paths = [path.replace("\\", "/").strip('\r\n') for path in paths]
    else:
        full_paths = [os.path.join(dirname, path).replace("\\", "/").strip('\r\n') for path in paths]
    return full_paths

def m3u_writer(name, current_folder, paths):
    for path in paths:
        if not path.startswith(current_folder):
            absolute = True
            break
        else:
            absolute = False
            
    if not absolute:
        paths = [path.lstrip(current_folder+'/').replace("/", "\\")+'\r\n' for path in paths]
    else:
        paths = [path +'\r\n' for path in paths]
    
    m3u_file = open(name, "w")
    map(m3u_file.write, paths)
    