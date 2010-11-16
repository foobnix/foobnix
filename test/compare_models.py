#-*- coding: utf-8 -*-
'''
Created on 16 нояб. 2010

@author: ivan
'''
from foobnix.regui.id3.audio import normilize_text
list = [
        "Мадонна - good",
        "Мадотта.mp3",
        "01 - Мадотта.mp3",
        "01 - Madonna - Sorry .flac",
        "1. Madonna - Прощай (some othe info).flac",
        "11.Madonna - Sorry ***some othe info).flac",
        ]

for line in list:
    print normilize_text(line) 
