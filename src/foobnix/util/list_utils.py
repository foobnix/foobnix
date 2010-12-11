#-*- coding: utf-8 -*-
'''
Created on Dec 7, 2010

@author: zavlab1
'''


def reorderer_list(List, new_index, old_index):
    if new_index < old_index:
        List.insert(new_index, List[old_index])
        del List[old_index + 1]
    elif old_index < new_index:
        List.insert(new_index + 1, List[old_index])
        del List[old_index]
    