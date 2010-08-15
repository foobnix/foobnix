'''
Created on 15  2010

@author: ivan
'''
from __future__ import with_statement
import os
from foobnix.util import LOG
from foobnix.util.configuration import FOOBNIX_TMP_RADIO


FOOBNIX_DIR = (os.getenv("HOME") or os.getenv('USERPROFILE')) + "/.foobnix"
FOOBNIX_DIR_RADIO = FOOBNIX_TMP_RADIO

EXTENSION = ".fpl"


class FPL():
    def __init__(self, name, urls_dict):
        self.name = name;
        self.urls_dict = urls_dict;
        
    def __str__(self):
        return self.name + "radios" + str(self.lines_dict)

class RadioFolder():
    
    def __init__(self):
        self.results = []
    
    """get list of foobnix playlist files in the directory"""
    def get_radio_list(self):
        if not os.path.isdir(FOOBNIX_DIR_RADIO):
            LOG.warn("Not a folder ", FOOBNIX_DIR_RADIO)
            return None
        
        result = []
        """read directory files by extestion and size > 0 """
        for item in os.listdir(FOOBNIX_DIR_RADIO):
            path = os.path.join(FOOBNIX_DIR_RADIO, item)
            if item.endswith(EXTENSION) and os.path.isfile(path) and os.path.getsize(path) > 0:
                LOG.info("Find radio station playlist", item)
                result.append(item)
        return result
    
    """parser playlist by name"""
    def parse_play_list(self, list_name):
        path = os.path.join(FOOBNIX_DIR_RADIO, list_name)
        if not os.path.isfile(path):
            LOG.warn("Not a file ", path)    
            return None
        
        dict = {}
        
        """get name and stations"""
        with open(path) as file:
            for line in file:
                if  line or not line.startswith("#") and "=" in line:                
                    name_end = line.find("=")
                    name = line[:name_end].strip()
                    stations = line[name_end + 1:].split(",")
                    if stations:
                        good_stations = []
                        for url in stations:
                            good_url = url.strip()
                            if good_url and (good_url.startswith("http://") or good_url.startswith("file://")):
                                if not good_url.endswith("wma"):
                                    if not good_url.endswith("asx"):                                
                                        if not good_url.endswith("ram"):
                                            good_stations.append(good_url)
                                            dict[name] = good_stations
        return dict
        
   
    
    def get_radio_FPLs(self):
        if self.results:
            LOG.info("Folder with radio already read")
            return self.results
        
        names = self.get_radio_list()
        
        if not names:
            return []
        
        results = []    
        for play_name in names:
            content = self.parse_play_list(play_name)
            LOG.info("Create FPL", play_name)
            play_name = play_name[:-len(EXTENSION)]
            results.append(FPL(play_name, content))
        return results
    
        


    
