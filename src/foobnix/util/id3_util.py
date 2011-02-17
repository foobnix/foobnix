#-*- coding: utf-8 -*-
'''
Created on 24 нояб. 2010

@author: ivan
'''
import os
import logging

from mutagen.mp4 import MP4
from foobnix.cue.cue_reader import update_id3_for_cue
from foobnix.util.image_util import get_image_by_path
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.util.bean_utils import update_bean_from_normalized_text
from foobnix.util.file_utils import file_extension, get_file_extension
from foobnix.util.fc import FC
from foobnix.util.audio import get_mutagen_audio


def decode_cp866(text):
    try:
        decode_text = text.decode("cp866")
        if decode_text.find(u"├") >= 0 :
            #LOG.warn("File tags encoding is very old cp866")
            text = decode_text.replace(
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
            #fix ёш to ё
            text = text.replace(u'\u0451\u0448', u'\u0451')
    except:
        pass
    return text

def udpate_id3_for_beans(beans):
    for bean in beans:
        if get_file_extension(bean.text) in FC().audio_formats:
            try:
                udpate_id3(bean)
            except Exception, e:
                logging.warn("update id3 error - " + e)
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
            else:
                if audio.has_key('artist'): bean.artist = decode_cp866(audio["artist"][0])
                if audio.has_key('title'): bean.title = decode_cp866(audio["title"][0])
                if audio.has_key('album'): bean.album = decode_cp866(audio["album"][0])
        #if audio and audio.has_key('tracknumber'): bean.tracknumber = audio["tracknumber"][0]
        #else: 
            #if audio and not audio.has_key('tracknumber'): 
        
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
    bean.size = os.path.getsize(bean.path)
    if info.__dict__.has_key('bitrate'):
        list[1] = str(info.bitrate/1000) + ' kbps'
        list[3] = convert_seconds_to_text(int(info.length))
    else:
        kbps = int(round(bean.size*8/info.length/1000))
        list.insert(1, str(kbps+1 if kbps % 2 else kbps) + ' kbps')
        list[2] = convert_seconds_to_text(int(info.length))
    size = '%.2f MB' % (float(bean.size)/1024/1024)
    list.append(size)
    return " | ".join(list)

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

def update_id3_wind_filtering(beans):
    beans = get_support_music_beans_from_all(beans)
    beans = udpate_id3_for_beans(beans)
    beans = update_id3_for_cue(beans)
    beans = add_upadte_image_paths(beans)
    result = []
    for bean in beans:
        result.append(bean)
    return result
