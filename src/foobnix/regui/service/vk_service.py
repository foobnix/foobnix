# -*- coding: utf-8 -*-
'''
Created on Sep 29, 2010

@author: ivan
'''
import re
import sys
import time
import urllib
import logging
import simplejson

from foobnix.regui.model import FModel
from foobnix.util.text_utils import html_decode
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.helpers.window import ChildTopWindow
import gtk
import webkit
from foobnix.fc.fc import FC

#FIN BUG IN PYTHON 2.7
#http://bugs.python.org/issue11703
if sys.version_info > (2, 6):
    from foobnix.thirdparty import urllib2
    from foobnix.thirdparty.urllib2 import HTTPError, URLError
else:
    import urllib2

class VKAuthorizationWindow(ChildTopWindow):
    REDIRECT_URL = "http://android.foobnix.com/vk"
    def __init__(self, service):
        self.service = service
        ChildTopWindow.__init__(self, _("VKontakte Authorization (require for music search)"), 640, 480)
        
        vbox = gtk.VBox(False, 0)
        self.access_token = None
        
        default_button = gtk.Button("Get Default Login Password")
        default_button.connect("clicked", self.on_defauls)
        
        self.web_view = webkit.WebView()
    
        
        url = "http://api.vkontakte.ru/oauth/authorize?client_id=2234333&scope=26&redirect_uri=" + self.REDIRECT_URL + "&response_type=token"
    
        self.web_view.load_uri(url)
        self.web_view.connect("navigation-policy-decision-requested", self._nav_request_policy_decision_cb)
        
               
        vbox.pack_start(self.web_view, True, True)
        vbox.pack_start(default_button, False, False)
        self.add(vbox)
    
    def get_response(self, line):
        id = line.find("#")
        fragment = line[id + 1:]
        res = {}
        for line in fragment.split("&"):
            key = line.split('=')[0]
            val = line.split('=')[1]
            res[key] = val
        
        return res

    def _nav_request_policy_decision_cb(self, view, frame, net_req, nav_act, pol_dec):
        uri = net_req.get_uri()       
        logging.debug("response url" + uri) 
        if "access_token" in uri:
            FC().access_token = self.get_response(uri)["access_token"]
            FC().user_id= self.get_response(uri)["user_id"]
            logging.debug("access token is " + FC().access_token)
            self.service.connect(FC().access_token, FC().user_id)
            FC().save()
            self.hide()
             
        return False
        
    def on_defauls(self, *a):
        f = urllib.urlopen("http://android.foobnix.com/vk", "")
        result = f.read().split(":")
        self.web_view.execute_script("javascript:(function() {document.getElementsByName('email')[0].value='%s'})()" % result[0])
        self.web_view.execute_script("javascript:(function() {document.getElementsByName('pass')[0].value='%s'})()" % result[1])           

        
    
class VKService:
    def __init__(self, token, user_id):
        self.vk_window = VKAuthorizationWindow(self)
        self.token = token
        self.user_id = user_id
        #self.is_show_authorization()
        
    def connect(self, token, user_id):
        self.token = token
        self.user_id = user_id
    
        
        
    def get_result(self, method, data):
        result  = self.get(method, data)
        object = self.to_json(result)        
        return object["response"]
        
    def get(self, method, data):
        time.sleep(0.6)
        #data = urllib.quote(data.encode('utf-8'))
        url = "https://api.vkontakte.ru/method/%(METHOD_NAME)s?%(PARAMETERS)s&access_token=%(ACCESS_TOKEN)s" % {'METHOD_NAME':method, 'PARAMETERS':data, 'ACCESS_TOKEN':self.token }
        logging.debug("GET" + url)
        response = urllib.urlopen(url)
        result = response.read()
        logging.debug("get VK API result", result)
        return  result
    
    def to_json(self, json):
        json_code = html_decode(json) 
        return simplejson.loads(json_code)
    
    def is_show_authorization(self):
        if not self.is_connected():
            self.vk_window.show()
            return True
        return False
        
    def is_connected(self):
        if not self.token or not self.user_id:
            return False
        
        res = self.get("getProfiles", "uid="+self.user_id)
        if "error" in res:
            self.vk_window.show()            
            return False
        else:
            return True
        
    
    def find_tracks_by_query(self, query):
        if self.is_show_authorization():
            return 
        
        logging.info("start search songs" + query)
        
        list = self.get_result("audio.search", "q=" + query)
        childs = []
        for line in list[1:]:
          
            
            bean = FModel(line['artist'] + ' - ' + line['title'])
            bean.aritst = line['artist']
            bean.title = line['title']
            bean.time = convert_seconds_to_text(line['duration'])
            bean.path = line['url']
            childs.append(bean)
             
        return childs

    def find_tracks_by_url(self, url):
        logging.debug("Search By URL")
        
        index = url.rfind("#")
        if index > 0:
            url = url[:index]
        index = url.find("id=")
        if index < 0:
            return None
        
        id = url[index + 3:]
        id = int(id)
        if id > 0:
            results = self.get_result('audio.get', "uid="+id)
        else:
            results = self.get_result('audio.get', "gid="+abs(id))
            
        childs = []
        for line in results:
            bean = FModel(line['artist'] + ' - ' + line['title'])
            bean.aritst = line['artist']
            bean.title = line['title']
            bean.time = convert_seconds_to_text(line['duration'])
            bean.path = line['url']
            childs.append(bean)
             
       
        return childs 
        
    def find_one_track(self, query):        
        vkSongs = self.find_tracks_by_query(query)
        if not vkSongs:
            return None
        #We want the most common song, so we search it using the track duration
        times_count = {}
        for song in vkSongs:
            time = song.time
            if time in times_count:
                times_count[time] = times_count[time] + 1
            else:
                times_count[time] = 1 
        
        #get most relatives times time
        r_count = max(times_count.values())
        r_time = self.find_time_value(times_count, r_count)
        logging.info("Song time" + str(r_time))
        logging.info("Count of songs with this time" + str(r_count))
        
        for song in vkSongs:
            if song.time == r_time:        
                return song

        return vkSongs[0]

    def find_time_value(self, times_count, r_count):
        for i in times_count:
            if times_count[i] == r_count:
                return i
        return None 

if __name__ == '__main__':
    vk = VKAuthorizationWindow()
    vk.show()            
    gtk.main()
