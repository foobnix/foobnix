# -*- coding: utf-8 -*-
'''
Created on Sep 29, 2010

@author: ivan
'''
import time
import urllib
import logging
import simplejson

from foobnix.regui.model import FModel
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.helpers.window import ChildTopWindow
import gtk

from foobnix.fc.fc import FC
from foobnix.helpers.image import ImageBase
import os
from foobnix.helpers.pref_widgets import HBoxLableEntry

class VKAuthorizationWindow(ChildTopWindow):
    REDIRECT_URL = "http://www.foobnix.com/welcome/vk-token-user-id"
    API_URL = "http://api.vkontakte.ru/oauth/authorize?client_id=2234333&scope=audio,friends&redirect_uri=" + REDIRECT_URL + "&display=touch&response_type=token"
    
    def get_web_url(self):
        return "http://api.vkontakte.ru/oauth/authorize?client_id=2234333&scope=audio,friends&redirect_uri=http://api.vk.com/blank.html&display=page&response_type=token"
                             
    def __init__(self, service):
        self.service = service
        ChildTopWindow.__init__(self, _("VKontakte Authorization (require for music search)"))
        self.set_resizable(True)
        vbox = gtk.VBox(False, 0)
        self.access_token = None
        
        default_button = gtk.Button(_("Get Default Login Password"))
        default_button.connect("clicked", self.on_defaults)

        
        def web_kit_token():
            import webkit            
            self.web_view = webkit.WebView()
            self.web_view.set_size_request(640, -1) 
            
            self.web_view.load_uri(self.get_web_url())
            self.web_view.connect("navigation-policy-decision-requested", self._nav_request_policy_decision_cb)
               
            vbox.pack_start(self.web_view, True, True)
            vbox.pack_start(default_button, False, False)
        
       

        def dialog_token():
            self.set_keep_above(True)
            self.token = gtk.Entry() 
            self.set_size_request(550, -1)           
            self.user_id = gtk.Entry()
            if FC().user_id:
                self.user_id.set_text(FC().user_id) 
            
            link = gtk.LinkButton(self.API_URL,_("1: Generate token (push or open the link url in the browser)"))
            
            apply = gtk.Button(_("2: Apply Token"))
            apply.connect("clicked", self.on_apply)
            
            self.info_line = gtk.Label(_("Please generate token..."))
            
            vbox.pack_start(ImageBase("vk.png"), False, False)
            vbox.pack_start(link, False, False)
            
            vbox.pack_start(HBoxLableEntry(gtk.Label(_("Token:")) , self.token))
            vbox.pack_start(HBoxLableEntry(gtk.Label(_("User ID:")) , self.user_id))
            
            vbox.pack_start(apply, False, False)
            vbox.pack_start(self.info_line, False, False)
        
        if os.name == 'nt':
            dialog_token()
        else:
            try:
                web_kit_token()
            except:
                dialog_token()
    
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

    def on_apply(self, *a):
        token, user_id = self.token.get_text(), self.user_id.get_text()
        token = token.strip()
        user_id = user_id.strip()
        if token and user_id:
            if self.service.is_authentified(token, user_id):
                self.apply(token, user_id)
                self.hide()
            else:
                self.info_line.set_text(_("Token incorrect or expired"))                
        else:
            self.info_line.set_text(_("Token or user is empty"));
            
        
    
    def apply(self, access_token, user_id):
        FC().access_token = access_token
        FC().user_id= user_id        
        self.service.set_token_user(access_token, user_id)
        logging.debug("access token is " + str(access_token))
        
        FC().save()
        self.hide()
    
    def _nav_request_policy_decision_cb(self, view, frame, net_req, nav_act, pol_dec):
        uri = net_req.get_uri()       
        logging.debug("response url" + uri) 
        if "access_token" in uri:
            token = self.get_response(uri)["access_token"]
            userid= self.get_response(uri)["user_id"]
            self.apply(token, userid)   
            self.hide(); 
        return False
        
    def on_defaults(self, *a):
        url = "http://android.foobnix.com/vk"
        try:
            f = urllib.urlopen(url, "")
        except IOError:
            logging.error("Can't get default login and password because no response from " + url)
            return
        result = f.read().split(":")
        self.web_view.execute_script("javascript:(function() {document.getElementsByName('email')[0].value='%s'})()" % result[0])
        self.web_view.execute_script("javascript:(function() {document.getElementsByName('pass')[0].value='%s'})()" % result[1])           
        
    
class VKService:
    def __init__(self, token, user_id):
        self.set_token_user(token, user_id)
        self.vk_window=VKAuthorizationWindow(self)
        self.connected = None
    
    def set_token_user(self, token, user_id):
        self.token = token
        self.user_id = user_id
        
    def get_result(self, method, data):
        result  = self.get(method, data)
        if not result:
            return
        logging.debug("result " + result)
        object = self.to_json(result)
        if object.has_key("response"):        
            return object["response"]
        else:
            return None
        
    def get(self, method, data):
        time.sleep(0.6)
        url = "https://api.vkontakte.ru/method/%(METHOD_NAME)s?%(PARAMETERS)s&access_token=%(ACCESS_TOKEN)s" % {'METHOD_NAME':method, 'PARAMETERS':data, 'ACCESS_TOKEN':self.token }
        logging.debug("GET " + url)
        try:
            response = urllib.urlopen(url)
        except IOError:
            logging.error("Can't get response from " + url)
            return
        result = response.read()
        logging.debug("get VK API result ", result)
        return  result
    
    def to_json(self, json):
        logging.debug("json " + json)
        return simplejson.loads(json)
    
    def is_show_authorization(self):
        if not self.is_connected():
            self.vk_window.show()
            return True
        return False
    
    def show_vk(self):
        self.vk_window.show()
    
    def is_connected(self):
        
        
        if self.connected:
            return True
        
        if not self.token or not self.user_id:
            return False
        
        res = self.get("getProfiles", "uid="+self.user_id)
        if "error" in res:
            self.vk_window.show()            
            self.connected =  False
            return False
        else:
            self.connected =  True
            return True
    
    def get_profile(self):
        return self.get_result("getProfiles", "uid="+str(self.user_id))
        
    
    def is_authentified(self, token,user_id):
        self.token = token
        self.user_id = user_id
        res = self.get("getProfiles", "uid="+self.user_id)
        if "error" in res:
            return False
        else:
            return True
            
    
    def find_tracks_by_query(self, query):
        if self.is_show_authorization():
            return 
        
        logging.info("start search songs" + query)
        query = urllib.quote(query)
        
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
            results = self.get_result('audio.get', "uid="+str(id))
        else:
            results = self.get_result('audio.get', "gid="+str(abs(id)))
            
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
    vk = VKAuthorizationWindow(None)
    vk.show()            
    gtk.main()
