import time
import md5
import httplib
import urllib
class SCrobler():
    def md5(self, value):
        return md5.new(value).hexdigest()

    def getSession(self):
        server = "post.audioscrobbler.com"
        timestamp = str(int(time.time()))
        auth = self.md5(self.md5("desteni") + timestamp)
        server_page = "/?hs=true&p=1.2.1&c=foo&v=2.0&u=ivanivanenko&t=" + timestamp + "&a=" + auth
        
        
        conn = httplib.HTTPConnection(server)
        conn.request("GET", server_page)
        response = conn.getresponse()
        
        
        data = response.read()
        print data
        
        if data.startswith("OK"):            
            self.sessionID = data[2 : data.find("http://")]            
        elif data.startswith("BADAUTH"):
            print "Bad auther"
        return self.sessionID    
        

    def nowPlaying(self, artist, trackname):
        print "Now Playing is..."
        server = "post2.audioscrobbler.com:80"
        server_page = "/protocol_1.2?s=" + self.sessionID + "&a=" + artist + "&t=" + trackname + "&b=Title&l=233&n=01&m="
        
        print server + server_page
        
        conn = httplib.HTTPConnection(server)
        conn.request("POST", server_page)
        response = conn.getresponse()
        
        print "Response : ", response.status, response.reason
        
        data = response.read()
        print "Response data : ", data
    
    def submission(self, artist, trackname):        
        data = None       
        while True:            
            session = self.getSession()
            print "Get Session : ", session
            time.sleep(1)
            par = {
                   's': session,
                   'a[0]': artist,
                   't[0]': trackname,
                   'i[0]': str(int(time.time())),
                   'o[0]':'P',
                   'r[0]':'',
                   'l[0]':'220',
                   'b[0]':'Album title',
                   'n[0]':'1',
                   'm[0]':''
                    }
            time.sleep(0.5)
            params = urllib.urlencode(par)
            response = urllib.urlopen("http://post2.audioscrobbler.com:80/protocol_1.2", params)
            
            data = response.read()
            print "Response data:_" + data + "_"
            if data.strip() != "BADSESSION":
                break
                
        
scrobbler = SCrobler()      
#scrobbler.nowPlaying("Ocean_Shiver", "Horizons_of_loneliness")
#print scrobbler.getSession()
#print scrobbler.getSession()
scrobbler.submission("test2", "test2")     
  
        

