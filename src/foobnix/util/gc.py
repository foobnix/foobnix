#-*- coding: utf-8 -*-
'''
Created on 23 сент. 2010

@author: ivan
'''
import ConfigParser
class GlobalConfig():
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('foobnix.cfg')

        
