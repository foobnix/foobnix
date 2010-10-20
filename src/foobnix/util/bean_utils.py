#-*- coding: utf-8 -*-
'''
Created on 20 окт. 2010

@author: ivan
'''

def update_parent_for_beans(beans, parent):
    for bean in beans:
        bean.parent(parent)
    
