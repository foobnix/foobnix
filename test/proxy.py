import urllib2
class ProxyPasswordMgr:
    def __init__(self):
        self.user = self.passwd = None
    def add_password(self, realm, uri, user, passwd):
        self.user = user
        self.passwd = passwd
    def find_user_password(self, realm, authuri):
        return self.user, self.passwd

#http://spys.ru/proxylist/
proxy = "85.175.153.30:80"
user = None
password = None

proxy = urllib2.ProxyHandler({"http" : proxy})
proxy_auth_handler = urllib2.ProxyBasicAuthHandler(ProxyPasswordMgr())
proxy_auth_handler.add_password(None, None, user, password)
opener = urllib2.build_opener(proxy, proxy_auth_handler)
urllib2.install_opener(opener)

f = urllib2.urlopen("http://www.ukr.net")
data = f.read()
f.close()
print data
 
