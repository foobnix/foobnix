#-*- coding: utf-8 -*-
'''
Created on 25 сент. 2010

@author: ivan
'''
"""base class to comunicate beatween all controls"""


class FControl(object):
    def __init__(self, controls):
        self.controls = controls
