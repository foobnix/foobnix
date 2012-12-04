'''
Created on 2  2012

@author: Dmitry Kogura (zavlab1)
'''

import urllib2
import re


def load_urls_name_page():
    base = 'http://www.sky.fm'
    radios = []
    file = open("SKY.FM.fpl", "w")
    #lf = LyricsFinder("p", "class", "channel")
    result = urllib2.urlopen(base).read()
    #print result
    #lf.feed(result)
    #print '<p class="channel"><a href="%s"</a></p>' % "(\\w*)"
    #result = '''<p class="channel"><a href="/hit90s">90's Hits</a></p></a></p>'''

    links = re.findall('<p class="channel"><a href="([\s\S][^</]*)', result, re.IGNORECASE | re.UNICODE | re.M)
    if links:
        #print links
        #full_urls = [base + "/mp3" + link.replace('>', ' = ') ]
        for link in links:
            index = link.find(">")
            if index >= 0:
                name = link[index + 1 :]
                url = link[0 : index - 1]
                pls = name + " = " + base + "/mp3" + url + ".pls\n"
                print pls
                radios.append(pls)
        print radios
        map(file.write, radios)
    
'''require 'nokogiri'
require 'open-uri'

doc = Nokogiri::HTML open 'http://www.sky.fm/'

stations = {}

doc.css('.channel a').each do |a|
  stations[a.content] = a.attr 'href'
end

stations.sort.each do |k, v|
  puts "#{k} = http://www.sky.fm/mp3#{v}.pls"
end'''

if __name__ == '__main__':
    load_urls_name_page() 