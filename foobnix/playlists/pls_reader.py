'''
Created on Nov 15, 2013

@author: Viktor Suprun
'''

import logging

from foobnix.gui.model import FModel
from foobnix.util.file_utils import get_file_extension


class PLSReader:

    def __init__(self, path):
        self.path = path
        try:
            self.pls = open(unicode(path))
        except Exception as e:
            logging.error(str(e))
            self.pls = None

    def get_common_beans(self):
        if not self.pls:
            return []
        try:
            beans = []
            lines = self.pls.readlines()
            lines = [map(lambda x: x.strip(), l.split("=")) for l in lines if not l.strip().startswith("[")]
            playlist = {}
            for l in lines:
                playlist[l[0]] = l[1]
            for i in range(1, int(playlist["NumberOfEntries"])+1):
                si = str(i)
                if "File" + si in playlist:
                    bean = FModel(path=playlist["File" + si],
                                  text=playlist["Title" + si] if "Title" + si in playlist else playlist["File" + si]).add_is_file(True)
                    beans.append(bean)
            return beans

        except Exception as e:
            logging.error("Couldn't parse pls")
            logging.error(str(e))
        return []


def update_id3_for_pls(beans):
    result = []
    for bean in beans:
        if bean.path and get_file_extension(bean.path) in [".pls"]:
            reader = PLSReader(bean.path)
            plsbeans = reader.get_common_beans()
            for bean in plsbeans:
                result.append(bean)
        else:
            result.append(bean)
    return result