from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import os
from foobnix.util.time_utils import normilize_time
from foobnix.util import LOG

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
        
            if audio and audio.has_key('artist'): bean.artist = audio["artist"][0]
            if audio and audio.has_key('title'): bean.title = audio["title"][0]
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
                
            bean.time = normilize_time(bean.length)        
            
    return bean    

def update_all_id3(beans):
    result = []
    for bean in beans:
        result.append(udpate_id3(bean))
    return result
    

 
