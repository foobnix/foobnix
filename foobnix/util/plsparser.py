'''
Created on Mar 3, 2010

@author: ivan
'''
import urllib2

            
def getStationPath(url):
    print "get station"
    
    if not url:
        return None
    
    _file_url = url
    urls = [] 
    try:       
        connect = urllib2.urlopen(url)
        data = connect.read()
        urls = getStations(data, urls)
    except:
        print "INCORRECT URL ERROR .... ", url
    return urls[0]
        
def getStations(data, urls):
    for line in data.rsplit():
        line = line.lower()         
        if line.startswith("file"):                                
                index = line.find("=")
                url = line[index + 1 : ]
                print url
                urls.append(url)
                return urls    
                

def getPlsName(_file_url):
    index = _file_url.rfind("/")
    return _file_url[index + 1:]

def getFirst(self, urls):
    if urls:
        return urls[0]
    else:
        return None
