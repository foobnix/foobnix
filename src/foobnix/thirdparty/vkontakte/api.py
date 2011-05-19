# coding: utf-8
import urllib
import warnings
from hashlib import md5
from functools import partial
import simplejson
import logging
import time

try:
    import json
except ImportError:
    import simplejson as json

API_URL = 'http://api.vk.com/api.php'
DEFAULT_TIMEOUT = 1

class VKError(Exception):
    __slots__ = ["code", "description", "params"]
    def __init__(self, code, description, params):
        self.code, self.description, self.params = (code, description, params)
        Exception.__init__(self, str(self))
    def __str__(self):
        return "Error(code = '%s', description = '%s', params = '%s')" % (self.code, self.description, self.params)

def _to_utf8(s):
    if isinstance(s, unicode):
        return s.encode('utf8')
    return s # this can be number, etc.

def signature(api_secret, params):
    keys = sorted(params.keys())
    param_str = "".join(["%s=%s" % (str(key), _to_utf8(params[key])) for key in keys])
    return md5(param_str+str(api_secret)).hexdigest()

def signature1(mid, params, secret):
    keys = sorted(params.keys())
    param_str = "".join(["%s=%s" % (str(key), _to_utf8(params[key])) for key in keys])
    url = str(mid) + param_str + str(secret)
    return md5(url).hexdigest()


def _sig(api_secret, **kwargs):
    msg = 'vkontakte.api._sig is deprecated and will be removed. Please use `vkontakte.signature`'
    warnings.warn(msg, DeprecationWarning, stacklevel=2)
    return signature(api_secret, kwargs)


def request(api_id, api_secret, opener, method, json,timestamp=None, timeout=DEFAULT_TIMEOUT, **kwargs):
    
    params = dict(
        api_id = str(api_id),
        method = method,
        v = '3.0',
        format = 'JSON',
        #sid = json['sid']
        #random = random.randint(0, 2**30),
        #timestamp = timestamp or int(time.time())
    )
    params.update(kwargs)
    params['sig'] = signature1(json['mid'], params,json['secret'])
    params['sid'] = json['sid']
    #params['sig'] = signature(api_secret, params)
    data = urllib.urlencode(params)
    # urllib2 doesn't support timeouts for python 2.5 so
    # custom function is used for making http requests
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    #print API_URL, data, headers, timeout
    return opener.open(API_URL, data).read()
    #print  http.post(API_URL, data, headers, timeout)
    #return http.post(API_URL, data, headers, timeout)


class API(object):
    def __init__(self, api_id, api_secret,opener, **defaults):
        self.api_id = api_id
        self.api_secret = api_secret
        self.opener = opener
        self.defaults = defaults
        self.method_prefix = ''
        
        url = opener.open("http://vkontakte.ru/login.php?app=2234333&layout=popup&type=browser&settings=26")
        url = url.geturl()
        
        logging.debug(url)    
        url = urllib.url2pathname(url)    
        id = url.find("session=")
        url = url[id+len("session="):]
    
        logging.debug(url)
        try:
            self.json =  simplejson.loads(url)
        except Exception, e:
            logging.error("Error decoding url %s" % url)
        logging.debug(json)
        self.my_user_id =self.json['mid'] 
        

    def get(self, method, timeout=DEFAULT_TIMEOUT, **kwargs):
        time.sleep(0.5)
        response = request(self.api_id, self.api_secret,self.opener, method,self.json, timeout = timeout, **kwargs)
        #if not (status >= 200 and status <= 299):
        #    raise VKError(status, "HTTP error", kwargs)
        data = json.loads(response)
        if "error" in data:
            raise VKError(data["error"]["error_code"], data["error"]["error_msg"], data["error"]["request_params"])
        return data['response']

    def __getattr__(self, name):

        # support for api.secure.<methodName> syntax
        if (name=='secure'):
            api = API(self.api_id, self.api_secret, **self.defaults)
            api.method_prefix = 'secure.'
            return api

        # the magic to convert instance attributes into method names
        return partial(self, method=name)

    def __call__(self, **kwargs):
        method = kwargs.pop('method')
        params = self.defaults.copy()
        params.update(kwargs)
        return self.get(self.method_prefix + method, **params)

