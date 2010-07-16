# -*- coding: utf-8 -*-
'''
Created on Jul 16, 2010

@author: ivan
'''
import urllib2
import re
site = "http://guzei.com/online_radio/?search=france"
def load_urls_name_page():
    
    file = open("GUZEI.COM.fpl", "w")
    
    for j in xrange(33):
        j = j + 1;
        
        site ="http://guzei.com/online_radio/?p="+str(j);
            
        connect = urllib2.urlopen(site)
        data = connect.read()  
        result = {}  
        
        for line in data.split("\n"):
            #print line
            reg_all = "([^{</}]*)"
          
            all = '<a href="./listen.php\?online_radio_id=([0-9]*)" target="guzei_online" title="'+reg_all+'"><span class="name">'+reg_all+'</span></a>'
            all1 ='<a href="./listen.php\?online_radio_id=([0-9]*)" target="guzei_online">'+reg_all+'</a>'
            links = re.findall(all, line, re.IGNORECASE | re.UNICODE)
            links1 = re.findall(all1, line, re.IGNORECASE | re.UNICODE)
            
            if links:
                i = 0
                for line in links:
                    id = line[0]
                    name = line[2] +" - "+ str(links1[i][1])
                    i+=1
                    url = get_ulr_by_id(id)
                    res =  name + " = " + url
                    print j
                    print res
                    file.write(res + "\n")
                    
                
    file.close()
                
                    
                
        

def get_ulr_by_id(id):
    url = "http://guzei.com/online_radio/listen.php?online_radio_id="+id
    connect = urllib2.urlopen(url)
    data = connect.read()
    for line in data.split("\n"):
        cr = 'Прямая ссылка на поток:'
        if line.find(cr) >= 0:
            link = line[line.find(cr)+len(cr):line.find('</p>')]
            link = link.strip()
            return link
    
          
            
            
        

#print get_ulr_by_id("5369")
load_urls_name_page()