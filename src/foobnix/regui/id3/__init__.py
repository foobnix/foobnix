# ~*~ coding:utf-8 ~*~ #
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import os
from foobnix.util.time_utils import normilize_time
from foobnix.util import LOG

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

def udpate_id3(bean):
    if bean and bean.path and os.path.isfile(bean.path):
        path_lower = bean.path.lower()
        audio = None
        if path_lower.endswith(".mp3"):
            try:
                audio = MP3(bean.path, ID3=EasyID3)
            except Exception, e:
                LOG.error("ID3 NOT MP3", e, bean.path)
                return bean

            if audio and audio.has_key('artist'): bean.artist = decode_cp866(audio["artist"][0])
            if audio and audio.has_key('title'): bean.title = decode_cp866(audio["title"][0])
            if audio and audio.has_key('tracknumber'): bean.tracknumber = audio["tracknumber"][0]
            if audio.info and audio.info.length: bean.length = int(audio.info.length)

            if audio.info:
                bean.info = audio.info.pprint()

            if bean.artist and bean.title:
                bean.text = bean.artist + " - " + bean.title

            if bean.tracknumber and bean.tracknumber.find("/") >= 0:
                bean.tracknumber = bean.tracknumber[:bean.tracknumber.find("/")]

            if bean.tracknumber and bean.tracknumber.startswith("0"):
                bean.tracknumber = bean.tracknumber[1:]

            if bean.tracknumber:
                try:
                    bean.tracknumber = int(bean.tracknumber)
                except:
                    bean.tracknumber = ""

            bean.time = normilize_time(bean.length)

    return bean

def update_all_id3(beans):
    result = []
    for bean in beans:
        result.append(udpate_id3(bean))
    return result



