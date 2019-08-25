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

def get_song_key(song_name):
    # sort by song number if possible, alphabetically otherwise
    num = get_song_number(song_name)
    if num is None:
        if song_name and ord(song_name[0]) < ord('0'):
            num = -10000
        else:
            num = 10000
    return (num, song_name)

def sort_by_song_name(list):
    list.sort(key=get_song_key)
    return list
