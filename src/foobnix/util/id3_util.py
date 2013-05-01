#-*- coding: utf-8 -*-
'''
Created on 24 нояб. 2010

@author: ivan
'''
from _bsddb import api
import chardet
import os
import re
import logging

from foobnix.thirdparty.mutagen.mp4 import MP4
from foobnix.thirdparty.mutagen.id3 import ID3
from foobnix.thirdparty.mutagen.flac import FLAC
from foobnix.fc.fc import FC, FCache
from foobnix.fc.fc_cache import COVERS_DIR
from foobnix.util.image_util import get_image_by_path
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.util.bean_utils import update_bean_from_normalized_text
from foobnix.util.file_utils import file_extension, get_file_extension
from foobnix.util.audio import get_mutagen_audio
from subprocess import Popen, PIPE
from zlib import crc32
from gi.repository.GdkPixbuf import Pixbuf
from tempfile import NamedTemporaryFile

RUS_ALPHABITE = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"


def decode_cp866(text):
    """
    Deprecated
    """
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
    """
    Deprecated
    """
    """del figures, punctuation marks and unrecognized text (so as cp866)"""
    only_alphabite = re.sub('[\d\W]', '', text)

    '''del only figures and punctuation marks'''
    without_punctuation = re.sub('[\d.,/_\-\^#$%&*()+=<>;:\'\"|]', '', text)

    """if unrecognized characters are more half of all 
    alphabetic characters, very likely code text is cp866"""
    return len(only_alphabite) <= len(without_punctuation)/2


def correct_encoding(text):
    try:
        text = text.encode('cp1252').decode('cp1251')
    except:
        pass
    return text


def udpate_id3_for_beans(beans):
    for bean in beans:
        if get_file_extension(bean.text) in FC().audio_formats:
            try:
                udpate_id3(bean)
            except Exception, e:
                logging.warn("update id3 error - % s" % e)
        elif get_file_extension(bean.text) in FC().video_formats:
            list = ["ffmpeg", "-i", bean.path, "|", "grep", "1"]#, "|", "cut", "-d", "\' \'", "-f", "4", "|", "sed", "s/,//"
            ffmpeg = Popen(list, universal_newlines=True, stderr=PIPE)
            for line in ffmpeg.stderr:
                if line.strip().startswith('Duration:'):
                    bean.time = os.path.splitext(line.strip().split(" ")[1])[0]
                    break
        if bean.text:
            if (bean.text[0] == "/") or (len(bean.text)>1 and bean.text[1] == ":"):
                bean.text = os.path.basename(bean.text)
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
                if audio.has_key('artist'): bean.artist = correct_encoding(audio["artist"][0])
                if audio.has_key('title'): bean.title = correct_encoding(audio["title"][0])
                if audio.has_key('album'): bean.album = correct_encoding(audio["album"][0])
                if audio.has_key('composer'): bean.composer = correct_encoding(audio['composer'][0])
                if audio.has_key('cuesheet'): bean.cue = correct_encoding(audio['cuesheet'][0])
                if audio.has_key('tracknumber'):
                    if not FC().numbering_by_order:
                        bean.tracknumber = audio["tracknumber"][0]

        duration_sec = bean.duration_sec

        if not bean.duration_sec and audio.info.length:
            duration_sec = int(audio.info.length)

        if audio.info.__dict__:
            bean.info = normalized_info(audio.info, bean)

        if bean.artist or bean.title:
            if bean.artist and bean.title:
                pass
            elif bean.artist:
                bean.title = _("Unknown title")
            elif bean.title:
                bean.artist = _("Unknown artist")
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
        new_list.append(str(info.bitrate / 1000) + ' kbps')
    else:
        kbps = int(round(bean.size * 8 / info.length / 1000))
        new_list.append(str(kbps + 1 if kbps % 2 else kbps) + ' kbps')
    if info.__dict__.has_key('length'):
        new_list.append(convert_seconds_to_text(int(info.length)))
    size = '%.2f MB' % (float(bean.size) / 1024 / 1024)
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


def add_update_image_paths(beans):
    for bean in beans:
        if bean.path and bean.is_file:
            set_cover_from_tags(bean)
            if not bean.image:
                bean.image = get_image_by_path(bean.path)
    return beans


def _get_extension_by_mime(mime):
    if mime == "image/jpeg" or mime == "image/jpg":
        return ".jpg"
    elif mime == "image/png":
        return ".png"
    logging.warning("Unknown cover mime-type: %s" % mime)
    return None


def _get_pic_from_mp3(audio):
    apics = [k for k in audio.keys() if k.startswith("APIC:")]
    if apics:
        return audio[apics[0]]
    return None


def _get_pic_from_flac(audio):
    if audio.pictures:
        return audio.pictures[0]
    return None


def set_cover_from_tags(bean):
    try:
        ext = get_file_extension(bean.path)
        if ext == ".mp3":
            data = _get_pic_from_mp3(ID3(bean.path))
        elif ext == ".flac":
            data = _get_pic_from_flac(FLAC(bean.path))
        else:
            return None
        if data:
            filename = os.path.join(COVERS_DIR, str(crc32(bean.path)) + '.jpg')
            fd = NamedTemporaryFile()
            fd.write(data.data)
            pixbuf = Pixbuf.new_from_file(fd.name)
            pixbuf.savev(filename, "jpeg", ["quality"], ["90"])
            fd.close()
            bean.image = filename
            basename = os.path.splitext(os.path.basename(filename))[0]
            cache_dict = FCache().covers
            if basename in cache_dict:
                cache_dict[basename].append(bean.text)
            else:
                cache_dict[basename] = [bean.text]
            return filename

    except Exception, e:
        print e
        pass
    return None


