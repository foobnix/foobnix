import urllib
import os
import re
class GetAllDIFM:
    
    
    def __init__(self):
        conn = urllib.urlopen("http://www.sky.fm/play/datempolounge")
        result = []
        for line in conn.read().rsplit():
            line = line.lower()
            if line.find("http://") > 0:                                
                result.append(line)                
        print result        
    
    def process(self):
        folder = "radio/"
        
        for url in self.getPlayListsUrls():
            #url = "http://www.di.fm/mp3/discohouse.pls"
            name = self.getName(url)
            data = self.readPLS(url)
            
            self.createFile(folder, name, data)   
    
    def createFile(self, folder, name, data):
        try:        
            os.mkdir(folder)
            os.mkfifo(folder + name)
        except OSError:
            print "Directory And Exists"
            
        f = open(folder + name, "w")
        
        f.write(data)
        f.close() 
        print "Addded " + name
    
    def readPLS(self, url):
        conn = urllib.urlopen(url)
        return conn.read()   
      
    def getName(self, url):
        prefix = "http://www.di.fm/mp3/"        
        return url[len(prefix):]                  
                
    def getPlayListsUrls(self):
        conn = urllib.urlopen("http://di.fm")
        result = []
        for line in conn.read().rsplit():
            line = line.lower()
            if line.find(".pls") > 0 and line.find("mp3") > 0:
                line = line.replace('"', "")
                line = line.replace("href=/", "http://www.di.fm/")
                result.append(line)                
        return result
                         
#di = GetAllDIFM()
p = re.compile('http://')
search = p.search('23223, ,"http://scfire-dtc-aa02.stream.aol.com:80/stream/1013}, http://64.34.178.168:8001":19},,"http://scfire-dtc-aa02.stream.aol.com:80/stream/1013},')
print search
if search:
    print search.groups(0)
    print search.groups(1)
    print search.groups(2)
        




