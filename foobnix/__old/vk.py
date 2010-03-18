# -*- coding: utf-8 -*-
import urllib2
import urllib
import re

class Vkontakte:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.cookie = None

    def get_s_value(self):
        #Возвращает уникальный идентификатор, который выдается на домене login.vk.com
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
        return re.findall(r"name='s' id='s' value='(.*?)'", data.read())[0]

    def get_cookie(self):
        #Возвращает remixsid из куки
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

vk = Vkontakte('ivan.ivanenko@gmail.com', 'desteni')
print vk.get_cookie()
print vk.get_s_value()
