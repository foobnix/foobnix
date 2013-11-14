'''
Created on 15  2010

@author: ivan
'''
from __future__ import with_statement
import os
import sys
import logging


FOOBNIX_RADIO_PATHS = [
    os.path.join(sys.path[0], "share/foobnix/radio"),
    "share/foobnix/radio",
    "/usr/local/share/foobnix/radio",
    "/usr/share/foobnix/radio"
    ]
EXTENSION = ".fpl"


class FPL():
    def __init__(self, name, urls_dict):
        self.name = name
        self.urls_dict = urls_dict

    def __str__(self):
        return self.name + "radios" + str(self.urls_dict)


class RadioFolder():
    def __init__(self):
        pass

    """get list of foobnix playlist files in the directory"""
    def get_radio_list(self):
        result = []
        for cur_path in FOOBNIX_RADIO_PATHS:
            if os.path.isdir(cur_path):
                """read directory files by extestion and size > 0 """
                for item in os.listdir(cur_path):
                    path = os.path.join(cur_path, item)
                    if item.endswith(EXTENSION) and os.path.isfile(path) and os.path.getsize(path) > 0:
                        logging.info("Find radio station playlist " + str(item))
                        if item not in result:
                            result.append(item)
        return result

    """parser playlist by name"""
    def parse_play_list(self, list_name):
        for path in FOOBNIX_RADIO_PATHS:
            full_path = os.path.join(path, list_name)

            if not os.path.isfile(full_path):
                logging.debug("Not a file " + full_path)
                continue

            dict = {}

            """get name and stations"""
            with open(full_path) as file:
                for line in file:
                    if line and not line.startswith("#") and "=" in line:
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
        names = self.get_radio_list()
        if not names:
            return []

        results = []
        for play_name in names:
            content = self.parse_play_list(play_name)
            logging.info("Create FPL" + play_name)
            play_name = play_name[:-len(EXTENSION)]
            results.append(FPL(play_name, content))
        return results
