'''
Created on Mar 3, 2010

@author: ivan
'''
import urllib2
class PLSParser():
    def __init__(self, file_url):        
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
    
    def getFirst(self):
        if self.urls:
            return self.urls[0]
        else:
            return None