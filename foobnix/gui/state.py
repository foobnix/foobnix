#-*- coding: utf-8 -*-
'''
Created on 23 сент. 2010

@author: ivan
'''
class LoadSave(object):
    def __init__(self):
        pass

    def on_load(self):
        raise Exception("Method not defined on_load", self.__class__.__name__)

    def on_save(self):
        raise Exception("Method not defined on_save", self.__class__.__name__)


class Quitable(object):

    def on_quit(self):
        pass


class Filterable(object):

    def filter_by_file(self, value):
        pass

    def filter_by_folder(self, value):
        pass