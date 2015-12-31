'''
Created on Mar 3, 2010

@author: ivan
'''
import urllib2
import logging
from foobnix.util import LOG


"Get content of the url"
def get_content(url):
    if not url:
        return None

    try:       
        connect = urllib2.urlopen(url, timeout=7)
        data = connect.read()
        return data
    except:
        logging.error("INCORRECT URL ERROR .... " + url)
        return None
    
def is_valid_station(url):
    if not url:
        return None

    try:       
        connect = urllib2.urlopen(url, timeout=10)
        if connect.getcode() == 200:
            return True
        else:
            return False
    except:
        logging.error("INCORRECT URL ERROR .... " + url)
        return False    
    
            
def getStationPath(url):
    
    if not url:
        return None
    
    _file_url = url
    urls = [] 
    try:       
        connect = urllib2.urlopen(url, timeout=7)
        data = connect.read()
        urls = getStations(data, urls)
    except Exception, e:
        logging.error("INCORRECT URL ERROR .... " + url + str(e))
    if urls:
        return urls[0]
        
def getStations(data, urls):
    for line in data.rsplit():
        line = line.lower()         
        if line.startswith("file"):                                
                index = line.find("=")
                url = line[index + 1 : ]
                urls.append(url)
                return urls    

def get_radio_source(url):
    LOG.fprint(url)
    if url:          
        if url.lower().endswith(".pls"):                
            source_url = getStationPath(url)
            if source_url :          
                logging.info("Radio url " + source_url)      
                return  source_url                   
                
        elif url.lower().endswith(".m3u"):
            content = get_content(url)
            if not content:
                return None
            for line in content.rsplit():
                if line.startswith("http://") and is_valid_station(line):
                    logging.info("Radio url " + line)
                    return line
    
    logging.info("Radio url " + url)
    return url
             
                        
                     
                

def getPlsName(_file_url):
    index = _file_url.rfind("/")
    return _file_url[index + 1:]

def getFirst(self, urls):
    if urls:
        return urls[0]
    else:
        return None
