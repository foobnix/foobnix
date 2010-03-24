#!/usr/bin/python
#
# Peteris Krumins (peter@catonmat.net)
# http://www.catonmat.net  --  good coders code, great reuse
#
# http://www.catonmat.net/blog/python-library-for-google-search/
#
# Code is licensed under MIT license.
#

import random
import socket
import urllib
import urllib2
import httplib

BROWSERS = (
    # Top most popular browsers in my access.log on 2009.02.12
    # tail -50000 access.log |
    #  awk -F\" '{B[$6]++} END { for (b in B) { print B[b] ": " b } }' |
    #  sort -rn |
    #  head -20
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru-RU; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; ru-RU; rv:1.9.0.6) Gecko/2009011912 Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru-RU; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (X11; U; Linux i686; ru-RU; rv:1.9.0.6) Gecko/2009020911 Ubuntu/8.10 (intrepid) Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; ru-RU; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; ru-RU; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.48 Safari/525.19'
    
)

TIMEOUT = 5  # socket timeout

class BrowserError(Exception):
    def __init__(self, url, error):
        self.url = url
        self.error = error

class PoolHTTPConnection(httplib.HTTPConnection):
    def connect(self):
        """Connect to the host and port specified in __init__."""
        msg = "getaddrinfo returns an empty list"
        for res in socket.getaddrinfo(self.host, self.port, 0,
                                      socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                self.sock = socket.socket(af, socktype, proto)
                if self.debuglevel > 0:
                    print "connect: (%s, %s)" % (self.host, self.port)
                self.sock.settimeout(TIMEOUT)
                self.sock.connect(sa)
            except socket.error, msg:
                if self.debuglevel > 0:
                    print 'connect fail:', (self.host, self.port)
                if self.sock:
                    self.sock.close()
                self.sock = None
                continue
            break
        if not self.sock:
            raise socket.error, msg

class PoolHTTPHandler(urllib2.HTTPHandler):
    def http_open(self, req):
        return self.do_open(PoolHTTPConnection, req)

class Browser(object):
    def __init__(self, user_agent=BROWSERS[0], debug=False, use_pool=False):
        self.headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5'
        }
        self.debug = debug

    def get_page(self, url, data=None):
        handlers = [PoolHTTPHandler]
        opener = urllib2.build_opener(*handlers)
        if data: data = urllib.urlencode(data)
        request = urllib2.Request(url, data, self.headers)
        try:
            response = opener.open(request)
            return response.read()
        except (urllib2.HTTPError, urllib2.URLError), e:
            raise BrowserError(url, str(e))
        except (socket.error, socket.sslerror), msg:
            raise BrowserError(url, msg)
        except socket.timeout, e:
            raise BrowserError(url, "timeout")
        except KeyboardInterrupt:
            raise
        except:
            raise BrowserError(url, "unknown error")

    def set_random_user_agent(self):
        self.headers['User-Agent'] = random.choice(BROWSERS)
        return self.headers['User-Agent']

