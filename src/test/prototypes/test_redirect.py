import urllib2

cookie_processor = urllib2.HTTPCookieProcessor()
opener = urllib2.build_opener(cookie_processor)
urllib2.install_opener(opener)
url = opener.open("http://www.foobnix.com/test_base")
print url.geturl()
        
