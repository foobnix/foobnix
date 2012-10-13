#-*- coding: utf-8 -*-
'''
Created on 1 сент. 2010

@author: ivan
'''

import base64
import socket
import urllib
import httplib
import logging
import urllib2

from foobnix.fc.fc import FC

class ProxyPasswordMgr:
    def __init__(self):
        self.user = self.passwd = None
    def add_password(self, realm, uri, user, passwd):
        self.user = user
        self.passwd = passwd
    def find_user_password(self, realm, authuri):
        return self.user, self.passwd

def set_proxy_settings():
    if FC().proxy_enable and FC().proxy_url:
        #http://spys.ru/proxylist/
        proxy = FC().proxy_url
        user = FC().proxy_user
        password = FC().proxy_password
        
        logging.info("Proxy enable:"+ proxy+ user+ password)
        
        proxy = urllib2.ProxyHandler({"http" : proxy})
        proxy_auth_handler = urllib2.ProxyBasicAuthHandler(ProxyPasswordMgr())
        proxy_auth_handler.add_password(None, None, user, password)
        opener = urllib2.build_opener(proxy, proxy_auth_handler)
        urllib2.install_opener(opener)
    else:
        logging.info("Proxy not enable")
        opener = urllib2.build_opener()
        urllib2.install_opener(opener)
        

""" idea from http://code.activestate.com/recipes/456195/ """
class ProxyHTTPConnection(httplib.HTTPConnection):

    _ports = {'http' : 80, 'https' : 443}


    def request(self, method, url, body=None, headers={}):
        #request is called before connect, so can interpret url and get
        #real host/port to be used to make CONNECT request to proxy
        proto, rest = urllib.splittype(url)
        if proto is None:
            raise ValueError, "unknown URL type: %s" % url
        #get host
        host, rest = urllib.splithost(rest)
        #try to get port
        host, port = urllib.splitport(host)
        #if port is not defined try to get from proto
        if port is None:
            try:
                port = self._ports[proto]
            except KeyError:
                raise ValueError, "unknown protocol for: %s" % url
        self._real_host = host
        self._real_port = port
        path = urllib2.urlparse.urlparse(url).path
        httplib.HTTPConnection.request(self, method, path, body, headers)

    def connect(self):
        httplib.HTTPConnection.connect(self)
        #send proxy CONNECT request
        connmsg = 'CONNECT %s:%s HTTP/1.1\r\n' % (self._real_host, self._real_port)
        connmsg += 'Proxy-Connection: keep-alive\r\n'
        connmsg += 'Connection: keep-alive\r\n'
        connmsg += 'Host: %s\r\n' % self._real_host
        connmsg += 'User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en_us) AppleWebKit/525.27.1 (KHTML, like Gecko) Version/3.2.1 Safari/525.27.1\r\n'
        if FC().proxy_enable and FC().proxy_user:
            connmsg += 'Proxy-Authorization: Basic %s\r\n' % base64.b64encode('%s:%s' % (FC().proxy_user, FC().proxy_password))
        connmsg += '\r\n'
        logging.debug(connmsg)
        self.send(connmsg.encode('utf-8'))
        #expect a HTTP/1.0 200 Connection established
        response = self.response_class(self.sock, strict=self.strict, method=self._method)
        (version, code, message) = response._read_status()
        #probably here we can handle auth requests...
        if code != 200:
            #proxy returned and error, abort connection, and raise exception
            self.close()
            raise socket.error, "Proxy connection failed: %d %s" % (code, message.strip())
        #eat up header block from proxy....
        while True:
            #should not use directly fp probably
            line = response.fp.readline()
            logging.debug(line)
            if line == '\r\n': break


class ProxyHTTPSConnection(ProxyHTTPConnection):
    
    default_port = 443

    def __init__(self, host, port = None, key_file = None, cert_file = None, strict = None):
        ProxyHTTPConnection.__init__(self, host, port)
        self.key_file = key_file
        self.cert_file = cert_file
    
    def connect(self):
        ProxyHTTPConnection.connect(self)
        #make the sock ssl-aware
        ssl = socket.ssl(self.sock, self.key_file, self.cert_file)
        self.sock = httplib.FakeSocket(self.sock, ssl)
        
                                       
class ConnectHTTPHandler(urllib2.HTTPHandler):

    def __init__(self, proxy=None, debuglevel=0):
        self.proxy = proxy
        urllib2.HTTPHandler.__init__(self, debuglevel)

    def do_open(self, http_class, req):
        if self.proxy is not None:
            req.set_proxy(self.proxy, 'http')
        return urllib2.HTTPHandler.do_open(self, ProxyHTTPConnection, req)

"""this class not used""" 
class ConnectHTTPSHandler(urllib2.HTTPSHandler):

    def __init__(self, proxy=None, debuglevel=0):
        self.proxy = proxy
        urllib2.HTTPSHandler.__init__(self, debuglevel)

    def do_open(self, http_class, req):
        if self.proxy is not None:
            req.set_proxy(self.proxy, 'https')
        return urllib2.HTTPSHandler.do_open(self, ProxyHTTPSConnection, req)

def get_https_response(url):
    proxy = FC().proxy_url if FC().proxy_enable and FC().proxy_url else None
    opener = urllib2.build_opener(ConnectHTTPHandler(proxy))
    return opener.open(url)

if __name__ == '__main__':
    res =  get_https_response('https://mail.ru')
    print res.read()
