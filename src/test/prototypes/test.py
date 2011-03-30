from foobnix.thirdparty.urllib2 import OpenerDirector, BaseHandler, Request
from foobnix.thirdparty import urllib2
from urllib import unwrap, splittag

class MyOpenerDirector(OpenerDirector):
    def __init__(self):
        OpenerDirector.__init__(self)
    
class MyHTTPCookieProcessor(BaseHandler):
    def __init__(self):
        pass

    def http_request(self, request):
        print "request",request
        return request

    def http_response(self, request, response):
        print "response",response
        return response
    

    https_request = http_request
    https_response = http_response


myProcessor = MyHTTPCookieProcessor()
#opener = MyOpenerDirector()
opener = urllib2.build_opener(myProcessor)
#opener.add_handler(redirect_hadler)
urllib2.install_opener(opener)

class MyReq(Request):
    def __init__(self, url):
        self.original = unwrap(url)
        self.fragment = splittag(self.original)
        Request.__init__(self,url)
    
    def get_full_url(self):
        print "get_full_url", self.fragment 
        if self.fragment:    
            return '%s#%s' % (self.original, self.fragment)    
        else:    
            return self.original
    
req = MyReq("http://www.foobnix.com/test_base")
url = opener.open(req)
print url.geturl()


#print urllib.urlopen("http://16.foobnix-cms.appspot.com/test_base").geturl()
#print urllib2.urlopen("http://16.foobnix-cms.appspot.com/test_base").geturl()


