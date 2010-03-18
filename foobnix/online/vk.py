# -*- coding: utf-8 -*-
'''
Created on Mar 17, 2010

@author: ivan
'''
# -*- coding: utf-8 -*-
import urllib2
import urllib
import re
import gst
import time
from string import replace

# -*- coding: utf-8 -*-



class Vkontakte:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cookie = None

    def get_s_value(self):

        host = 'http://login.vk.com/?act=login'
        post = urllib.urlencode({'email' : self.email,
                                 'expire' : '',
                                 'pass' : self.password,
                                 'vk' : ''})

        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13 (.NET CLR 3.5.30729)',
                   'Host' : 'login.vk.com',
                   'Referer' : 'http://vkontakte.ru/index.php',
                   'Connection' : 'close',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache',
                  }

        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn)
        result = data.read()
        
        return re.findall(r"name='s' id='s' value='(.*?)'", result)[0]

    def get_cookie(self):

        if self.cookie: return self.cookie

        host = 'http://vkontakte.ru/login.php?op=slogin'
        post = urllib.urlencode({'s' : self.get_s_value()})
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
                   'Host' : 'vkontakte.ru',
                   'Referer' : 'http://login.vk.com/?act=login',
                   'Connection' : 'close',
                   'Cookie' : 'remixchk=5; remixsid=nonenone',
                   'Pragma' : 'no-cache',
                   'Cache-Control' : 'no-cache'
                  }
        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn)
        cookie_src = data.info().get('Set-Cookie')
        self.cookie = re.sub(r'(expires=.*?;\s|path=\/;\s|domain=\.vkontakte\.ru(?:,\s)?)', '', cookie_src)
        return self.cookie
    
    def get_page(self, query):
        host = 'http://vkontakte.ru/gsearch.php?section=audio&q=vasya#c[q]=some%20id&c[section]=audio'
        post = urllib.urlencode({
                                 "c[q]" : query,
                                 "c[section]":"audio"
                                })
        headers = {'User-Agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.13) Gecko/2009073022 Firefox/3.0.13',
                   'Host' : 'vkontakte.ru',
                   'Referer' : 'http://vkontakte.ru/index.php',
                   'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8',
                   'X-Requested-With' : 'XMLHttpRequest',
                   'Connection' : 'close',
                   'Cookie' : 'remixlang=0; remixchk=5; audio_vol=100; %s' % self.get_cookie(),
                   'Pragma' : 'no-cache',
                   'Cache-Control' : '    no-cache'
                  }
        conn = urllib2.Request(host, post, headers)
        data = urllib2.urlopen(conn);
        result = data.read()
        return result
    
def last_search_query(value):
    host = "http://en.vpleer.ru/?q=" + value
    data = urllib2.urlopen(host)
    return data.read()

vk = Vkontakte('ivan.ivanenko@gmail.com', '')
#vk.get_cookie()

page = """
    <img class="playimg" onclick="return operate(87939180, 4634, 38310345, '522b4844829d', 242);" id="imgbutton87939180" nosorthandle="true" src="images / play.gif">
    style=\\\"width: 18px; vertical-align:top\\\">\\n <img class=\\\"playimg\\\" onclick=\\\"return operate(85948082,4636,68974845,'4f6715c83b1b',250);\\\" id=\\\"imgbutton85948082\\\" nosorthandle=\\\"true\\\" 
    """
page = vk.get_page("Ария")
print page
resultall = re.findall("return operate\(([\w() ,']*)\);", page)
for result in resultall:
    result = replace(result, "'", " ")
    result = replace(result, ",", " ")
    
    result = result.split()
    "http://cs4634.vkontakte.ru/u38310345/audio/96859a617a23.mp3"
    print result
    if len(result) > 4:
        id_un1 = result[0]
        id_server = result[1]
        id_folder = result[2]
        id_file = result[3]
        id_un2 = result[3]
    
        url = "http://cs" + id_server + ".vkontakte.ru/u" + id_folder + "/audio/" + id_file + ".mp3"
        print url
