'''
Created on Mar 3, 2010

@author: ivan
'''
import urllib2
class PLSParser():
    def __init__(self, file_url):
        self._file_url = file_url
        self.urls = [] 
        try:       
            connect = urllib2.urlopen(file_url)
            data = connect.read()
            self.urls = self.getStations(data)
        except:
            print "INCORRECT URL ERROR .... ", file_url
        
    def getStations(self, data):
        for line in data.rsplit():
            line = line.lower()         
            if line.startswith("file"):                                
                    index = line.find("=")
                    url = line[index + 1 : ]
                    print url
                    self.urls.append(url)
                    return self.urls    
                    
    def getAllList(self):
        return self.urls
    
    def getPlsName(self):
        index = self._file_url.rfind("/")
        return self._file_url[index + 1:]
    
    def getFirst(self):
        if self.urls:
            return self.urls[0]
        else:
            return None
