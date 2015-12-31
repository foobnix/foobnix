
# -*- coding: utf-8 -*-
'''
Created on Sep 29, 2010

@author: ivan
'''
from foobnix.helpers.window import ChildTopWindow

import os
import gi
gi.require_version("WebKit", "3.0")

import threading
import time
import urllib
import logging
import urllib2
import simplejson

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import WebKit
from gi.repository import Soup

from HTMLParser import HTMLParser
from urlparse import urlparse
from foobnix.fc.fc import FC, FCBase
from foobnix.gui.model import FModel
from foobnix.fc.fc_helper import CONFIG_DIR
from foobnix.util.time_utils import convert_seconds_to_text

cookiefile = os.path.join(CONFIG_DIR, "vk_cooky")


class VKWebkitAuth(Gtk.Dialog, ChildTopWindow):

    SCOPE = ["audio", "friends", "wall"]
    CLIENT_ID = "2234333"

    def __init__(self):
        Gtk.Dialog.__init__(self, _("vk.com authorization"), None, Gtk.DialogFlags.MODAL, ())
        ChildTopWindow.__init__(self)
        self.set_size_request(550, -1)
        self.auth_url = "http://oauth.vk.com/oauth/authorize?" + \
                        "redirect_uri=http://oauth.vk.com/blank.html&response_type=token&" + \
                        "client_id=%s&scope=%s" % (self.CLIENT_ID, ",".join(self.SCOPE))
        self.web_view = WebKit.WebView()

        self.vbox.pack_start(self.web_view, False, False, 0)

        self.web_view.connect('resource-load-finished', self.on_load)
        session = WebKit.get_default_session()
        if FC().proxy_enable and FC().proxy_url:
            if FC().proxy_user and FC().proxy_password:
                proxy_url = "http://%s:%s@%s" % (FC().proxy_user, FC().proxy_password, FC().proxy_url)
            else:
                proxy_url = "http://%s" % FC().proxy_url
            soup_url = Soup.URI.new(proxy_url)
            session.set_property("proxy-uri", soup_url)
        else:
            session.set_property("proxy-uri", None)

        cookiejar = Soup.CookieJarText.new(cookiefile, False)
        session.add_feature(cookiejar)

        self.access_token = None
        self.user_id = None
        self.on_load_method_finished = False

    def auth_user(self, check_only=False):
        if check_only:
            return self.access_token, self.user_id if self.access_token and self.user_id else None
        self.web_view.load_uri(self.auth_url)
        logging.debug("waiting for answer...")
        while not (self.web_view.get_load_status().value_name == 'WEBKIT_LOAD_FINISHED' and self.on_load_method_finished):
            Gtk.main_iteration()
        logging.debug("answer found!")
        logging.debug(self.access_token)
        logging.debug(self.user_id)
        if self.access_token and self.user_id:
            return self.access_token, self.user_id
        self.web_view.show()
        result = self.run()
        if (result == Gtk.ResponseType.ACCEPT) and self.access_token and self.user_id:
            return self.access_token, self.user_id
        return None

    def extract_answer(self, url):
        def split_key_value(kv_pair):
            kv = kv_pair.split("=")
            if len(kv) == 2:
                return kv[0], kv[1]  # ["key", "val"], e.g. key=val
            else:
                return kv[0], None  # ["key"], e.g. key= or key
        return dict(split_key_value(kv_pair) for kv_pair in url.fragment.split("&"))

    def on_load(self, webview, frm, res):
        url = urlparse(webview.get_property("uri"))
        if url.path == "/blank.html":
            answer = self.extract_answer(url)
            if "access_token" in answer and "user_id" in answer:
                self.access_token, self.user_id = answer["access_token"], answer["user_id"]
            self.response(Gtk.ResponseType.ACCEPT)
        self.on_load_method_finished = True


class VKService:
    def __init__(self, token, user_id):
        self.set_token_user(token, user_id)
        self.authorized_lock = threading.Lock()

    def auth(self, check_only=False):
        logging.debug("do auth")
        self.auth_res = None
        self.task_finished = False

        def safetask():
            self.auth_res = False
            logging.debug("trying to auth")
            auth_provider = VKWebkitAuth()
            res = auth_provider.auth_user(check_only)
            auth_provider.destroy()
            if res:
                FC().access_token = res[0]
                FC().user_id = res[1]
                self.set_token_user(res[0], res[1])
                self.auth_res = True
            self.task_finished = True
            logging.debug("task finished, result is %s" % str(res))
        GLib.idle_add(safetask)
        logging.debug("idle task added, waiting...")
        while not self.task_finished:
            time.sleep(0.1)
        logging.debug("auth result is %s" % self.auth_res)
        return self.auth_res

    def set_token_user(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def get_result(self, method, data, attempt_count=0):
        logging.debug("get_result(%s, %s, %s)" % (method, data, attempt_count))
        result = self.get(method, data)
        if not result:
            return
        logging.debug("result " + result)
        try:
            object = self.to_json(result)
        except simplejson.JSONDecodeError, e:
            logging.error(e)
            return
        if "response" in object:
            return object["response"]
        elif "error" in object:
            logging.debug("error found!")
            if attempt_count > 0:
                return
            if not self.auth():
                return
            time.sleep(1)
            attempt_count += 1
            return self.get_result(method, data, attempt_count)

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
        p = HTMLParser()
        json = p.unescape(json)
        return simplejson.loads(json)

    def get_profile(self, without_auth=False):
        return self.get_result("getProfiles", "uid=" + str(self.user_id), 1 if without_auth else 0)

    def find_tracks_by_query(self, query):
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
            bean.path = line['url'].replace("https://", "http://")
            bean.vk_audio_id = "%s_%s" % (line['owner_id'], line['aid'])
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
            bean.path = line['url'].replace("https://", "http://")
            bean.vk_audio_id = "%s_%s" % (line['owner_id'], line['aid'])
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

    def find_track_by_id(self, id):
        if id is not None:
            parts = id.split("_")
            result = self.get_result("audio.get", "owner_id=%s&audio_ids=%s" % (str(parts[0]), str(parts[1])))
            line = result[1]
        else:
            result = self.get_result("audio.get", "audios=" + str(id))
            line = result[0]
        if not result:
            return None
        bean = FModel(line['artist'] + ' - ' + line['title'])
        bean.aritst = line['artist']
        bean.title = line['title']
        bean.time = convert_seconds_to_text(line['duration'])
        bean.path = line['url'].replace("https://", "http://")
        bean.vk_audio_id = "%s_%s" % (line['owner_id'], line['aid'])
        return bean


    def find_time_value(self, times_count, r_count):
        for i in times_count:
            if times_count[i] == r_count:
                return i
        return None

    def add(self, bean):
         if (bean.vk_audio_id != None):
             ids=bean.vk_audio_id.split('_')
             url = "https://api.vk.com/method/audio.add?access_token=%(ACCESS_TOKEN)s&aid=%(AID)s&oid=%(OID)s" % {'ACCESS_TOKEN':self.token, 'AID':ids[1], 'OID':ids[0] }
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
