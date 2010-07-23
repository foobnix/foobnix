'''
Created on Jul 16, 2010

@author: ivan
'''
import urllib2

site = "http://www.screamer-radio.com/"
site_full = site + "directory/browsegenre/51/"

def load_urls_name_page():
    connect = urllib2.urlopen(site_full)
    data = connect.read()  
    file = open("SKY.FM.fpl", "w")
    for line in data.split("\n"):
        if line.find("sky.fm") > 0:            
            url = line[line.find('<td><a href="')+len('<td><a href="')+1:line.find('/">')]
            name = line[line.find('sky.fm -')+len('sky.fm -')+1:line.find('</a></td>')]
            LOG.info(name, url
            urls = get_urls(site + url)
            file.write(name.strip() + " = " + urls + "\n");
    file.close()       

def get_urls(path):
    connect = urllib2.urlopen(path)
    data = connect.read()
    result = ""  
    for line in data.split("\n"):
        if line.find(") http://") >0:
           result = result + line[line.find(') ') +2:line.find("<br />")]+", "

    return result[:-2]
load_urls_name_page()
#LOG.info(get_urls("http://www.screamer-radio.com/directory/show/3825/")