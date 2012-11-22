
# -*- coding: utf-8 -*-
'''
Created on Sep 29, 2010

@author: ivan
'''

import os
import gtk
import time
import thread
import urllib
import gobject
import logging
import urllib2
import simplejson

from foobnix.fc.fc import FC
from foobnix.regui.model import FModel
from foobnix.fc.fc_helper import CONFIG_DIR
from foobnix.util.const import ICON_FOOBNIX
from foobnix.helpers.image import ImageBase
from foobnix.helpers.pref_widgets import HBoxLableEntry
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name


class VKAuthorizationWindow(gtk.Dialog):
    REDIRECT_URL = "http://www.foobnix.com/welcome/vk-token-user-id"
    API_URL = "http://api.vk.com/oauth/authorize?client_id=2234333&scope=audio,friends&redirect_uri=" + REDIRECT_URL + "&display=touch&response_type=token"
    
    def get_web_url(self):
        return "http://api.vk.com/oauth/authorize?client_id=2234333&scope=audio,friends&redirect_uri=http://api.vk.com/blank.html&display=page&response_type=token"
   
    def show(self):
        super(VKAuthorizationWindow, self).show()
                            
    def __init__(self, service):
        self.service = service
        gtk.Dialog.__init__(self, _("VKontakte Authorization (is required for music search)"))
        self.set_resizable(True)
        self.access_token = None
        try:
            self.set_icon_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))
        except TypeError: pass

        
        def web_kit_token():
            import webkit
            import ctypes
            
            self.web_view = webkit.WebView()
            self.web_view.set_size_request(640, -1) 
                        
            libgobject = ctypes.CDLL('libgobject-2.0.so.0')
            libsoup = ctypes.CDLL('libsoup-2.4.so.1')
            self.libwebkit = ctypes.CDLL('libwebkitgtk-1.0.so.0')
            self.session = self.libwebkit.webkit_get_default_session()
            
            if  FC().proxy_enable and FC().proxy_url:
                libgobject = ctypes.CDLL('libgobject-2.0.so.0')
                libsoup = ctypes.CDLL('libsoup-2.4.so.1')
                self.libwebkit = ctypes.CDLL('libwebkitgtk-1.0.so.0')
                if FC().proxy_user and FC().proxy_password:
                    full_proxy = "http://%s:%s@%s" % (FC().proxy_user, FC().proxy_password, FC().proxy_url)
                else:
                    full_proxy = "http://%s" % FC().proxy_url
                proxy_uri = libsoup.soup_uri_new(full_proxy) # set your proxy url
                libgobject.g_object_set(self.session, "proxy-uri", proxy_uri, None)
            else:
                libgobject.g_object_set(self.session, "proxy-uri", None, None)
            #'''remove all cookiejars'''
            #generic_cookiejar_type = libgobject.g_type_from_name('SoupCookieJar')
            #libsoup.soup_session_remove_feature_by_type(session, generic_cookiejar_type)

            '''and replace with a new persistent jar'''
            self.cooky_file = os.path.join(CONFIG_DIR, "vk_cooky")
            cookiejar = libsoup.soup_cookie_jar_text_new(self.cooky_file, False)
            libsoup.soup_session_add_feature(self.session, cookiejar)    
            
            self.web_view.load_uri(self.get_web_url())
            self.web_view.connect("navigation-policy-decision-requested", self._nav_request_policy_decision_cb)
            self.web_view.connect("load-finished", self.load_finished)
            
            self.web_view.show()   
            self.vbox.pack_start(self.web_view, True, True)
            
            
        def dialog_token():
            self.set_keep_above(True)
            self.token = gtk.Entry() 
            self.set_size_request(550, -1)           
            self.user_id = gtk.Entry()
            if FC().user_id:
                self.user_id.set_text(FC().user_id) 
            
            edit = gtk.Entry()
            edit.set_text(self.API_URL)
            link = gtk.LinkButton(self.API_URL,_("Open"))
            
            line = gtk.HBox(False, 0)                    
            line.pack_start(edit, True, True)
            line.pack_start(link, False, False)
            
            apply = gtk.Button(_("2: Apply Token"))
            apply.connect("clicked", self.on_dt_apply)
            
            self.info_line = gtk.Label(_("Please generate token..."))
            
            self.vbox.pack_start(ImageBase("vk.png"), False, False)
            self.vbox.pack_start(line, False, False)
            
            self.vbox.pack_start(HBoxLableEntry(gtk.Label(_("Token:")) , self.token))
            self.vbox.pack_start(HBoxLableEntry(gtk.Label(_("User ID:")) , self.user_id))
            
            self.vbox.pack_start(apply, False, False)
            self.vbox.pack_start(self.info_line, False, False)
        
        if os.name == 'nt':
            dialog_token()
        else:
            try:
                web_kit_token()
            except Exception, e:
                logging.error(str(e))
                dialog_token()
                pass
   
    def get_response(self, line):
        id = line.find("#")
        fragment = line[id + 1:]
        res = {}
        for line in fragment.split("&"):
            key = line.split('=')[0]
            val = line.split('=')[1]
            res[key] = val
        
        return res

    def on_dt_apply(self, *a):
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

        thread.start_new_thread(FC().save, ())
        self.hide()
        self.response(gtk.RESPONSE_APPLY)
        
    def load_finished(self, *a):
        pass
        
        
    def _nav_request_policy_decision_cb(self, view, frame, net_req, nav_act, pol_dec):
        uri = net_req.get_uri()  
        if "access_token" in uri:
            token = self.get_response(uri)["access_token"]
            userid= self.get_response(uri)["user_id"]
            self.apply(token, userid)
        elif "error" in uri:
            logging.error("error in response: " + uri)
            self.hide()
        elif "login?act=blocked" in uri:
            logging.warning("blocked in response: " + uri)
            self.service.reset_vk()
            zavlab_string = "<html><body><p>The login is blocked</p></body></html>"
            self.web_view.load_html_string(zavlab_string, "file:///")
        return False
        

class VKService:
    def __init__(self, token, user_id):
        self.set_token_user(token, user_id)
        self.vk_window=VKAuthorizationWindow(self)
        self.connected = None
    
    def set_token_user(self, token, user_id):
        self.token = token
        self.user_id = user_id
        
    def get_result(self, method, data, attempt_count=0):
        result  = self.get(method, data)
        if not result:
            return
        logging.debug("result " + result)
        if "error" in result:
            if attempt_count:
                return
            logging.info("Try to get new access token and search again")
            self.vk_window.libwebkit.soup_session_abort(self.vk_window.session)
            gobject.idle_add(self.vk_window.web_view.load_uri, self.vk_window.get_web_url())
            time.sleep(3)
            attempt_count += 1
            return self.get_result(method, data, attempt_count)
        try:
            object = self.to_json(result)
        except simplejson.JSONDecodeError, e:
            logging.error(e)
            return
        if object.has_key("response"):        
            return object["response"]
    
    def reset_vk(self):
        if os.path.isfile(self.vk_window.cooky_file):
            os.remove(self.vk_window.cooky_file)
        
        FC().access_token = None
        FC().user_id = None
        self.token = None
        self.user_id = None
        self.connected =  False  

    def get(self, method, data):
        url = "https://api.vk.com/method/%(METHOD_NAME)s?%(PARAMETERS)s&access_token=%(ACCESS_TOKEN)s" % {'METHOD_NAME':method, 'PARAMETERS':data, 'ACCESS_TOKEN':self.token }
        logging.debug("Try to get response from vkontakte")
        try:
            response = urllib2.urlopen(url, timeout=7)
            if not vars().has_key("response"):
                logging.error("Can't get response from vkontakte")
                return
        except IOError:
            logging.error("Can't get response from vkontakte")
            return
        result = response.read()
        return result
    
    def to_json(self, json):
        logging.debug("json " + json)
        return simplejson.loads(json)
    
    def is_authorized(self):
        self.result = None

        def task_is_authorized():
            if self.is_connected():
                self.result = True
                return
            self.vk_window = VKAuthorizationWindow(self)
            response = self.vk_window.run()
            if response == gtk.RESPONSE_APPLY:
                self.vk_window.destroy()
                self.result = True
            else:
                self.vk_window.destroy()
                self.result = False

        gobject.idle_add(task_is_authorized)
        while self.result == None:
            time.sleep(0.3)
        return self.result

    def show_vk(self):
        self.vk_window.show()
    
    def is_connected(self):
                
        if self.connected:
            return True
        
        if not self.token or not self.user_id:
            return False
        
        res = self.get("getProfiles", "uid="+self.user_id)
        if not res:
            self.connected =  False
            return False
        elif "error" in res:
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
        def post():
            self.find_tracks_by_query(self, query)
        
        if not self.is_authorized():
            return
        
        logging.info("start search songs " + query)
        query = urllib.quote(query.encode("utf-8"))
        
        list = self.get_result("audio.search", "q=" + query)
        childs = []
        
        if not list:
            return childs

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
        logging.info("Song time " + str(r_time))
        logging.info("Count of songs with this time " + str(r_count))
        
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
