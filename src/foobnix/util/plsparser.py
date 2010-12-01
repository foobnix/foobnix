'''
Created on Mar 3, 2010

@author: ivan
'''
import urllib2
from foobnix.util import LOG


"Get content of the url"
def get_content(url):
    if not url:
        return None

    try:       
        connect = urllib2.urlopen(url)
        data = connect.read()
        return data
    except:
        LOG.error("INCORRECT URL ERROR .... ", url)
        return None
    
            
def getStationPath(url):
    
    if not url:
        return None
    
    _file_url = url
    urls = [] 
    try:       
        connect = urllib2.urlopen(url)
        data = connect.read()
        urls = getStations(data, urls)
    except Exception, e:
        LOG.error("INCORRECT URL ERROR .... ", url, e)
    if urls:
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

def get_radio_source(url):
    if url:          
        if url.lower().endswith(".pls"):                
            source_url = getStationPath(url)
            LOG.info("Radio content", source_url)
            if source_url :          
                LOG.info("Radio url", source_url)      
                return  source_url                   
                
        elif url.lower().endswith(".m3u"):
            content = get_content(url)
            LOG.info("Radio content", content)
            if not content:
                return None
            for line in content.rsplit():
                if line.startswith("http://"):
                    LOG.info("Radio url", line)
                    return line
    
    LOG.info("Radio url", url)
    return url
             
                        
                     
                

def getPlsName(_file_url):
    index = _file_url.rfind("/")
    return _file_url[index + 1:]

def getFirst(self, urls):
    if urls:
        return urls[0]
    else:
        return None
