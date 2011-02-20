#-*- coding: utf-8 -*-
'''
Created on Dec 7, 2010

@author: zavlab1
'''
import re
def reorderer_list(List, new_index, old_index):
    if new_index < old_index:
        List.insert(new_index, List[old_index])
        del List[old_index + 1]
    elif old_index < new_index:
        List.insert(new_index + 1, List[old_index])
        del List[old_index]


def any(pred, list):
    for el in list:
        if pred(el):
            return True
    return False

def get_song_number(text):
    res = re.search('^([0-9]{1,4})', text)
    if res:
        return int(res.group())

def comparator(x, y):
    value_x = get_song_number(x)
    value_y = get_song_number(y)
    if value_x and value_y:
        return value_x - value_y
    else:
        return cmp(x, y)

def sort_by_song_name(list):
    list.sort(comparator)
    return list
