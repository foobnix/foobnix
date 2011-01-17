'''
Created on 16  2010

@author: ivan
'''
import urllib2
import logging
site = "http://myradio.ua/"


def load_urls_name_page():
    connect = urllib2.urlopen(site)
    data = connect.read()  
    result = {}  
    file = open("MYRADIO_UA.fpl", "w")
    for line in data.split("\n"):
        line = line.decode("cp1251")
        pre = "<a href=\"chanel/";
        start = line.find(pre)
        end = line.find("</a>", start + 10)
        if start > 0 and end > 0:                        
            url = line[line.find("<a href=\"") + len(" < a href"):line.find(">", start)].replace('"', '')
            name = line[line.find(">", start) + 1:line.find("</a>")]
            result[url.strip()] = name
            
                        
            urls = get_radio_ulr(url.strip()).split(",")
            line = name.strip() + " = " + urls[1] + ", " + urls[0]
            file.write(line + "\n");
            logging.info(line)
            
            if url.strip() == "chanel/eurovision":
                file.close()
                return result
        

def get_radio_ulr(chanel):
    connect = urllib2.urlopen(site + chanel)
    data = connect.read()
    result = "" 
    for line in data.rsplit("\n"):
        """<img class="roll" src="http://img.myradio.com.ua/img/center/big_listen_icons/winamp_low_out.jpg">"""
        if line.find('<img class="roll" src="') > 0 and line.find('.m3u') and  line.find("window") < 0 :
            pre = '<div class="but"><a href="'
            index_pre = line.find(pre)
            url = line[index_pre + len(pre): line.find('.m3u', index_pre)]
            url = site + url + ".m3u"
            result = result + url + ", "
    return result[:-2]
            
             


