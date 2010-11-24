#-*- coding: utf-8 -*-
'''
Created on 20 окт. 2010

@author: ivan
'''
from foobnix.util.audio import normilize_text

def update_parent_for_beans(beans, parent):
    for bean in beans:
        bean.parent(parent)
    

"""update bean info form text if possible"""
def update_bean_from_normilized_text(bean):
    
    if not bean.artist or not bean.title:
        bean.text = normilize_text(bean.text)            
        
        text_artist = bean.get_artist_from_text()
        text_title = bean.get_title_from_text()
          
        if text_artist and text_title:
            bean.artist, bean.title = text_artist, text_title
    return bean

