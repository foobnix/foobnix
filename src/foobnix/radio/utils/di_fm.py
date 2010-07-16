'''
Created on 16  2010

@author: ivan
'''
import urllib2
site = "http://di.fm"
def load_urls_name_page():
    connect = urllib2.urlopen(site)
    data = connect.read()  
    result = {}  
    file = open("DI_FM.fpl", "w")
    for line in data.split("\n"):
        pre = '<td><a href="http://listen.di.fm/public3/'
        if line.find(pre) > 0:
            el = "<td><a href=\""
            url = line[line.find(el) + len(el) :line.find("\" rel")]
            print url
            name = url[url.rfind("/") + 1:]
            name = name[:-4]
            print 
            file.write(name + " = " + url + "\n")
            
    file.close()
        
load_urls_name_page()
