'''
Created on Apr 26, 2013

@author: dimitry
'''

import logging
import os.path

from foobnix.gui.model import FModel
from foobnix.util.file_utils import get_file_extension


class M3UReader:
    def __init__(self, path):
        self.path = path
        try:
            self.m3u = open(unicode(path))
        except Exception as e:
            logging.error(str(e))
            self.m3u = None

    def get_common_beans(self):
        paths_and_texts = self.parse()
        if not paths_and_texts:
            return []
        beans = [FModel(path=path_and_text[0],
                        text=path_and_text[1])
                        .add_is_file(True)
                        for path_and_text in paths_and_texts]
        return beans

    def parse(self):
        try:
            if not self.m3u:
                return
            lines = self.m3u.readlines()
            paths = [os.path.normpath(line).strip('\r\n') for line in lines
                     if line.startswith("##") or not line.startswith("#")]
            dirname = os.path.dirname(self.path)

            full_paths = []
            paths = iter(paths)
            for path in paths:
                text = None
                if path.startswith("##"):
                    def task(path):
                        text = path[2 : ]
                        try:
                            next_path = paths.next()
                            path = next_path if not next_path.startswith("##") else None
                        except StopIteration:
                            path = None
                            next_path = None
                        if not path:
                            full_paths.append( [path, text.strip('\r\n')] )
                            if next_path:
                                path, text = task(next_path)

                        return path, text

                    path, text = task(path)
                    if not path:
                        break

                if text:
                    text = text.strip('\r\n')
                else:
                    new_text = path.rsplit('/', 1)[-1]
                    if path == new_text:
                        text = path.rsplit('\\', 1)[-1]
                    else:
                        text = new_text

                if (path in "\\/"):
                    full_paths.append( [path.replace("\\", "/"), text] )
                elif path.startswith('http'):
                    if not text:
                        text = path.rsplit('/', 1)[-1]
                    full_paths.append( [path.replace('/', '//', 1), text] )
                else:
                    full_paths.append([os.path.join(dirname, path).replace("\\", "/"), text] )
            return full_paths
        except IndexError:
            logging.warn("You try to load empty playlist")



def update_id3_for_m3u(beans):
    result = []
    for bean in beans:
        if bean.path and get_file_extension(bean.path) in [".m3u", ".m3u8"]:
            reader = M3UReader(bean.path)
            m3u_beans = reader.get_common_beans()
            for bean in m3u_beans:
                result.append(bean)
        else:
            result.append(bean)
    return result