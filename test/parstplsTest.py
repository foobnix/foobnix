import urllib2

class PLSParser():
    def __init__(self, file_url):
        self._file_url = file_url         
        open = urllib2.urlopen(file_url)
        
        self.urls = []
        for line in open.read().rsplit():
            line = line.lower()         
            if line.startswith("file"):                                
                    index = line.find("=")
                    url =  line[index +1 : ]
                    print url
                    self.urls.append(url)
                    
    def getAllList(self):
        return self.urls
    
    def getPlsName(self):
        index = self._file_url.rfind("/")
        return self._file_url[index+1:]
    
    def getFirst(self):
        if self.urls:
            return self.urls[0]
        else:
            return None
        
parser = PLSParser("http://www.di.fm/mp3/chilloutdreams.pls")
print parser.getPlsName()        