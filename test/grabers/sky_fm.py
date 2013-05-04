'''
Created on 2 dec 2012

@author: Dmitry Kogura (zavlab1)
'''

import re
import urllib2

def load_urls_name_page():
    base = 'http://www.sky.fm'
    radios = []
    file = open("SKY.FM.fpl", "w")
    result = urllib2.urlopen(base).read()
    links = re.findall('<p class="channel"><a href="([\s\S][^</]*)', result, re.IGNORECASE | re.UNICODE | re.M)
    if links:
        for link in links:
            index = link.find(">")
            if index >= 0:
                name = link[index + 1 :]
                url = link[0 : index - 1]
                pls = name + " = " + base + "/mp3" + url + ".pls\n"
                print pls
                radios.append(pls)

        map(file.write, radios)
    

if __name__ == '__main__':
    load_urls_name_page() 