#-*- coding: utf-8 -*-
'''
Created on July 18, 2012

@author: zavlab1
'''

def crop_string(string, max_length):
    if (max_length > -1) and (len(string) > max_length):
            return string[:max_length]
    else:
            return string