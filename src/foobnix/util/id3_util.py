#-*- coding: utf-8 -*-
'''
Created on 24 нояб. 2010

@author: ivan
'''
import os
import re
import logging

from mutagen.mp4 import MP4
from foobnix.fc.fc import FC
from foobnix.util.image_util import get_image_by_path
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.util.bean_utils import update_bean_from_normalized_text
from foobnix.util.file_utils import file_extension, get_file_extension

from foobnix.util.audio import get_mutagen_audio

RUS_ALPHABITE = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"


def decode_cp866(text):
    try:
        for i in text:
            if i.lower() in RUS_ALPHABITE:
                return text
        
        if not is_cp866(text):
            return text
             
        decode_text = text.decode('cp866')
        
        if u"├" in decode_text:   
            decode_text = decode_text.replace(
                        u"\u252c", u'ё').replace(
                        u"├", "").replace(
                        u"░", u"р").replace(
                        u"▒", u"с").replace(
                        u"▓", u"т").replace(
                        u"│", u"у").replace(
                        u"┤", u"ф").replace(
                        u"╡", u"х").replace(
                        u"╢", u"ц").replace(
                        u"╖", u"ч").replace(
                        u"╕", u"ш").replace(
                        u"╣", u"щ").replace(
                        u"║", u"ъ").replace(
                        u"╗", u"ы").replace(
                        u"╝", u"ь").replace(
                        u"╜", u"э").replace(
                        u"╛", u"ю").replace(
                        u"┐", u"я")
            decode_text = decode_text.replace(u'\u0451\u0448', u'\u0451')
        return decode_text
    except:
        pass
    return text

def is_cp866(text):
    '''del figures, punctuation marks and unrecognized text (so as cp866)'''
    only_alphabite = re.sub('[\d\W]', '', text)
    
    '''del only figures and punctuation marks'''
    without_punctuation = re.sub('[\d.,/_\-\^#$%&*()+=<>;:\'\"|]', '', text)
    
    """if unrecognized characters are more half of all 
    alphabetic characters, very likely code text is cp866"""
    return len(only_alphabite) <= len(without_punctuation)/2

def udpate_id3_for_beans(beans):
    for bean in beans:
        if get_file_extension(bean.text) in FC().audio_formats:
            try:
                udpate_id3(bean)
            except Exception, e:
                logging.warn("update id3 error - % s" % e)
    return beans

def udpate_id3(bean):
    if bean and bean.path and os.path.isfile(bean.path):
        try:
            audio = get_mutagen_audio(bean.path)            
        except Exception, e:
            logging.warn("ID3 NOT MP3" + str(e) + bean.path)
            return bean
        
        if audio:
            if isinstance(audio, MP4):
                if audio.has_key('\xa9ART'): bean.artist = audio["\xa9ART"][0]
                if audio.has_key('\xa9nam'): bean.title = audio["\xa9nam"][0]
                if audio.has_key('\xa9alb'): bean.album = audio["\xa9alb"][0]
                if audio.has_key('\xa9wrt'): bean.composer = audio["\xa9wrt"][0]
                if audio.has_key('trkn'): 
                    if not FC().numbering_by_order:
                        bean.tracknumber = audio['trkn'][0]
            else:
                if audio.has_key('artist'): bean.artist = decode_cp866(audio["artist"][0])
                if audio.has_key('title'): bean.title = decode_cp866(audio["title"][0])
                if audio.has_key('album'): bean.album = decode_cp866(audio["album"][0])
                if audio.has_key('composer'): bean.composer = decode_cp866(audio['composer'][0])
                if audio.has_key('tracknumber'):
                    if not FC().numbering_by_order:
                        bean.tracknumber = audio["tracknumber"][0]   
        
        duration_sec = bean.duration_sec
        
        if not bean.duration_sec and audio.info.length:
            duration_sec = int(audio.info.length)
        
        if audio.info.__dict__:
            bean.info = normalized_info(audio.info, bean)
                       
        if bean.artist and bean.title:
            bean.text = bean.artist + " - " + bean.title
        
        if bean.tracknumber:
            try:
                bean.tracknumber = int(bean.tracknumber)
            except:
                bean.tracknumber = ""
        
        bean = update_bean_from_normalized_text(bean)
            
        bean.time = convert_seconds_to_text(duration_sec)
        
    return bean

def normalized_info(info, bean):
    list = info.pprint().split(", ")
    new_list = []
    bean.size = os.path.getsize(bean.path)
    new_list.append(list[0])
    if info.__dict__.has_key('channels'):
        new_list.append('Ch: ' + str(info.channels))
    if info.__dict__.has_key('bits_per_sample'):
        new_list.append(str(info.bits_per_sample) + ' bit')
    if info.__dict__.has_key('sample_rate'):
        new_list.append(str(info.sample_rate) + 'Hz')
    if info.__dict__.has_key('bitrate'):
        new_list.append(str(info.bitrate/1000) + ' kbps')
    else:
        kbps = int(round(bean.size*8/info.length/1000))
        new_list.append(str(kbps+1 if kbps % 2 else kbps) + ' kbps')
    if info.__dict__.has_key('length'):
        new_list.append(convert_seconds_to_text(int(info.length)))
    size = '%.2f MB' % (float(bean.size)/1024/1024)
    new_list.append(size)
    return " | ".join(new_list)

def get_support_music_beans_from_all(beans):
    result = []
    for bean in beans:
        if bean.path and os.path.isdir(bean.path):
            result.append(bean)
        elif bean.path and os.path.isfile(bean.path) and file_extension(bean.path) in FC().audio_formats:
            result.append(bean)
        elif bean.path and bean.path.startswith("http://"):
            result.append(bean)
        else:
            result.append(bean)
    
    return result


def add_upadte_image_paths(beans):
    for bean in beans:
        if bean.path:
            bean.image = get_image_by_path(bean.path)
    return beans


