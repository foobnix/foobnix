
# -*- coding: utf-8 -*-
'''
Created on Sep 29, 2010

@author: ivan
'''

import os
import gtk
import threading
import time
import thread
import urllib
import gobject
import logging
import urllib2
import simplejson
import cookielib
import tempfile

from HTMLParser import HTMLParser
from urlparse import urlparse
from foobnix.fc.fc import FC, FCBase
from foobnix.regui.model import FModel
from foobnix.fc.fc_helper import CONFIG_DIR
from foobnix.util.const import ICON_FOOBNIX
from foobnix.helpers.image import ImageBase
from foobnix.helpers.pref_widgets import HBoxLableEntry
from foobnix.util.time_utils import convert_seconds_to_text
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name

cookiefile = os.path.join(CONFIG_DIR, "vk_cooky")


class FormParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.url = None
        self.params = {}
        self.in_form = False
        self.in_warn = False
        self.form_parsed = False
        self.method = "GET"
        self.captcha_image = None
        self.auth_error = None

    """Magic below"""
    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict((name.lower(), value) for name, value in attrs)
        if tag == "div" and "class" in attrs and "warn" in attrs["class"]:
            self.in_warn = True
            return

        if tag == "form":
            if self.form_parsed:
                raise RuntimeError("Second form on page")
            if self.in_form:
                raise RuntimeError("Already in form")
            self.in_form = True
        if not self.in_form:
            return
        if tag == "form":
            self.url = attrs["action"]
            if "method" in attrs:
                self.method = attrs["method"]
        elif tag == "input" and "type" in attrs and "name" in attrs:
            if attrs["type"] in ["hidden", "text", "password"]:
                self.params[attrs["name"]] = attrs["value"] if "value" in attrs else ""
        elif tag == "img" and "src" in attrs and "captcha.php" in attrs["src"]:
            self.captcha_image = attrs["src"]

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "div" and self.in_warn:
            self.in_warn = False
        elif tag == "form":
            if not self.in_form:
                raise RuntimeError("Unexpected end of <form>")
            self.in_form = False
            self.form_parsed = True

    def handle_data(self, data):
        if self.in_warn:
            self.auth_error = data


class VKAuth(gtk.Dialog):

    SCOPE = ["audio", "friends", "wall"]
    CLIENT_ID = "2234333"

    def __init__(self):
        super(VKAuth, self).__init__(_("vk.com authorization"), None, gtk.DIALOG_MODAL,
                                     (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT, gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        """INIT GUI"""
        self.hwparrer = gtk.HBox(False, 0)
        self.vwrapper = gtk.VBox(False, 0)
        self.lhbox = gtk.HBox(False, 5)
        self.phbox = gtk.HBox(False, 5)
        self.rhbox = gtk.HBox(False, 5)
        self.chbox = gtk.HBox()

        self.error_label = gtk.Label()

        self.login = gtk.Entry()
        self.password = gtk.Entry()
        self.captcha_image = gtk.Image()
        self.vkimage = gtk.Image()
        self.captcha = gtk.Entry()
        self.remember = gtk.CheckButton()

        self.vkimage.set_from_file(get_foobnix_resourse_path_by_name("vk-small.png"))

        self.password.set_visibility(False)
        self.password.set_invisible_char("*")

        login_label = gtk.Label(_("Email"))
        self.lhbox.pack_start(login_label, False, False, 0)
        self.lhbox.pack_start(self.login, True, True, 0)

        password_label = gtk.Label(_("Password"))
        self.phbox.pack_start(password_label, False, False, 0)
        self.phbox.pack_start(self.password, True, True, 0)

        self.rhbox.pack_start(gtk.Label(_("Remember password")), False, False, 0)
        self.rhbox.pack_start(self.remember, False, False, 0)

        self.chbox.pack_start(self.captcha_image, False, False, 0)
        self.chbox.pack_start(self.captcha, True, True, 0)

        self.vwrapper.pack_start(self.lhbox, False, False, 4)
        self.vwrapper.pack_start(self.phbox, False, False, 4)
        self.vwrapper.pack_start(self.chbox, False, False, 4)

        self.hwparrer.pack_start(self.vkimage, True, True, 0)
        self.hwparrer.pack_start(self.vwrapper, False, True, 0)

        self.vbox.pack_start(self.error_label, False, False, 4)
        self.vbox.pack_start(self.hwparrer, False, False, 0)
        self.vbox.pack_start(self.rhbox, False, False, 4)
        self.vbox.show_all()

        """SET DEFAULT SIZES AND VISIBILITY"""
        [node.set_size_request(80, -1) for node in [login_label, password_label]]
        [node.hide() for node in [self.error_label, self.chbox]]

        self.login.set_text(FCBase().vk_login or "")
        self.password.set_text(FCBase().vk_password or "")
        self.remember.set_active(FCBase().vk_remember_password)

        """Build opener"""
        self.opener = self.build_opener()
        self.auth_url = "http://oauth.vk.com/oauth/authorize?" + \
                        "redirect_uri=http://oauth.vk.com/blank.html&response_type=token&" + \
                        "client_id=%s&scope=%s&display=wap" % (self.CLIENT_ID, ",".join(self.SCOPE))

    def do_save(self):
        if self.remember.get_active():
            FCBase().vk_login = self.login.get_text()
            FCBase().vk_password = self.password.get_text()
        else:
            FCBase().vk_login = None
            FCBase().vk_password = None
        FCBase().vk_remember_password = self.remember.get_active()

    def build_opener(self):
        cookiejar = cookielib.FileCookieJar(cookiefile)
        cookie_handler = urllib2.HTTPCookieProcessor(cookiejar)
        redirect_handler = urllib2.HTTPRedirectHandler()
        #proxy_handler = urllib2.ProxyHandler()
        #proxy_auth_handker = urllib2.ProxyBasicAuthHandler()
        return urllib2.build_opener(cookie_handler, redirect_handler)

    def extract_answer(self, url):
        def split_key_value(kv_pair):
            kv = kv_pair.split("=")
            if len(kv) == 2:
                return kv[0], kv[1]  # ["key", "val"], e.g. key=val
            else:
                return kv[0], None  # ["key"], e.g. key= or key
        return dict(split_key_value(kv_pair) for kv_pair in urlparse(url).fragment.split("&"))

    def get_page_by_url(self, url, params=None):
        if params:
            params = urllib.urlencode(params)
        response = self.opener.open(url, params)
        page = response.read()
        parser = FormParser()
        parser.feed(page)
        parser.close()
        return response, parser

    def auth_user(self, check_only=False):
        res, parser = self.get_page_by_url(self.auth_url)
        parsedurl = urlparse(res.geturl())
        if parsedurl.path == "/blank.html":
            """user already authorized or error"""
            answer = self.extract_answer(res.geturl())
            if "access_token" in answer and "user_id" in answer:
                return answer["access_token"], answer["user_id"]
        elif parsedurl.path == "/oauth/authorize" and "grant_access" in parser.url:
            logging.debug("Grant access page without authorization")
            return
        elif parsedurl.path != "/oauth/authorize":
            logging.debug("Someting wrong")
            logging.debug(parsedurl.path)
            return
        if check_only:
            return
        """Full auth"""
        return self.do_full_auth(res, parser)

    def do_full_auth(self, res, parser):
        logging.debug("do full auth")
        if parser.captcha_image:
            logging.debug("captcha enabled, %s" % parser.captcha_image)
            cres = self.opener.open(parser.captcha_image)
            blob = cres.read()
            unknwn, image = tempfile.mkstemp()
            fd = os.open(image, os.O_RDWR)
            os.write(fd, blob)
            self.captcha_image.set_from_file(image)
            self.chbox.show()
        else:
            self.chbox.hide()
        if parser.auth_error:
            logging.debug(parser.auth_error)
            self.error_label.set_text(parser.auth_error)
            self.error_label.show()
        else:
            self.error_label.hide()
        login, passw = FCBase().vk_login, FCBase().vk_password
        if not login or not passw or parser.captcha_image or parser.auth_error:
            dialog_result = self.run()
            self.captcha_image.clear()
            self.do_save()
            self.hide()
            if dialog_result is gtk.RESPONSE_ACCEPT.real:
                login = self.login.get_text()
                passw = self.password.get_text()
            else:
                return
        parser.params["email"] = login
        parser.params["pass"] = passw
        """send auth params"""
        new_res, new_parser = self.get_page_by_url(parser.url, parser.params)
        if new_parser.captcha_image or new_parser.auth_error:
            return self.do_full_auth(new_res, new_parser)
        else:
            """if access without confirmation"""
            answer = self.extract_answer(new_res.geturl())
            if "access_token" in answer and "user_id" in answer:
                return answer["access_token"], answer["user_id"]
            """do grant access"""
            new_res, new_parser = self.get_page_by_url(new_parser.url, new_parser.params)
            answer = self.extract_answer(new_res.geturl())
            if "access_token" in answer and "user_id" in answer:
                return answer["access_token"], answer["user_id"]
        logging.debug("something wrong...")
        return


class VKService:
    def __init__(self, token, user_id):
        self.set_token_user(token, user_id)
        self.connected = None
        self.authorized_lock = threading.Lock()

    def auth(self, check_only=False):
        self.connected = None
        auth_provider = VKAuth()
        res = auth_provider.auth_user(check_only)
        auth_provider.destroy()
        if res:
            FC().access_token = res[0]
            FC().user_id = res[1]
            #thread.start_new_thread(FC().save, ())
            self.set_token_user(res[0], res[1])
            self.connected = True
            return True
        return False
    
    def set_token_user(self, token, user_id):
        self.token = token
        self.user_id = user_id
        
    def get_result(self, method, data, attempt_count=0):
        result = self.get(method, data)
        if not result:
            return
        logging.debug("result " + result)
        if "error" in result:
            if attempt_count:
                return
            logging.info("Try to get new access token and search again")
            if not self.auth(True):
                return
            time.sleep(3)
            attempt_count += 1
            return self.get_result(method, data, attempt_count)
        try:
            object = self.to_json(result)
        except simplejson.JSONDecodeError, e:
            logging.error(e)
            return
        if "response" in object:
            return object["response"]
    
    def reset_vk(self):
        if os.path.isfile(cookiefile):
            os.remove(cookiefile)
        
        FC().access_token = None
        FC().user_id = None
        FCBase().vk_login = None
        FCBase().vk_password = None
        self.token = None
        self.user_id = None
        self.connected = False

    def get(self, method, data):
        url = "https://api.vk.com/method/%(METHOD_NAME)s?%(PARAMETERS)s&access_token=%(ACCESS_TOKEN)s" % {'METHOD_NAME':method, 'PARAMETERS':data, 'ACCESS_TOKEN':self.token }
        if (method == 'audio.search'):
            count = FC().search_limit
            url = url + "&count=%(COUNT)s" % {'COUNT': count }

        if (FC().enable_vk_autocomlete == True):
            url = url + "&auto_complete=1"
        else:
            url = url + "&auto_complete=0"

        #logging.debug("GET " + url)
        logging.debug("Try to get response from vkontakte")
        try:
            response = urllib2.urlopen(url, timeout=7)
            if "response" not in vars():
                logging.error("Can't get response from vkontakte")
                return
        except IOError:
            logging.error("Can't get response from vkontakte")
            return
        result = response.read()
        return result
    
    def to_json(self, json):
        logging.debug("json " + json)
        p = HTMLParser()
        json = p.unescape(json)
        return simplejson.loads(json)
    
    def is_authorized(self):
        self.authorized_lock.acquire()
        self.result = None

        def task_is_authorized():
            if self.is_connected():
                self.result = True
            elif self.auth():
                self.result = True
            else:
                self.result = False

        gobject.idle_add(task_is_authorized)
        while self.result is None:
            time.sleep(0.1)
        if self.authorized_lock.locked():
            self.authorized_lock.release()
        return self.result

    def show_vk(self):
        self.auth()
    
    def is_connected(self):
        if self.connected:
            return True
        
        if not self.token or not self.user_id:
            return False
        
        res = self.get("getProfiles", "uid=" + self.user_id)
        if not res:
            self.connected = False
            return False
        elif "error" in res:
            self.connected = False
            return False
        else:
            self.connected = True
            return True
    
    def get_profile(self):
        return self.get_result("getProfiles", "uid=" + str(self.user_id))

    def is_authentified(self, token, user_id):
        self.token = token
        self.user_id = user_id
        res = self.get("getProfiles", "uid=" + self.user_id)
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
            bean.aid = line['aid']
            bean.oid = line['owner_id']
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
            results = self.get_result('audio.get', "uid=" + str(id))
        else:
            results = self.get_result('audio.get', "gid=" + str(abs(id)))
            
        childs = []
        for line in results:
            bean = FModel(line['artist'] + ' - ' + line['title'])
            bean.aritst = line['artist']
            bean.title = line['title']
            bean.time = convert_seconds_to_text(line['duration'])
            bean.path = line['url']
            bean.aid = line['aid']
            bean.oid = line['owner_id']
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
                times_count[time] += 1
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

    def add(self, bean):
        if (bean.aid != None) & (bean.oid != None):
            url = "https://api.vk.com/method/audio.add?access_token=%(ACCESS_TOKEN)s&aid=%(AID)s&oid=%(OID)s" % {'ACCESS_TOKEN':self.token, 'AID':bean.aid, 'OID':bean.oid }
            #logging.debug("GET " + url)
            logging.debug("Try add audio to vkontakte")
            try:
                response = urllib2.urlopen(url, timeout=7)
                if "response" not in vars():
                    logging.error("Can't get response from vkontakte")
                    return
            except IOError:
                logging.error("Can't get response from vkontakte")
                return
            result = response.read()
        return result

