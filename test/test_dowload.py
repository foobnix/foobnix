'''
Created on Mar 25, 2010

@author: ivan
'''
import urllib2
    
remotefile = urllib2.urlopen('http://cs4713.vkontakte.ru/u20875334/audio/e357e0ad25c4.mp3')
print remotefile.info()
f = open("/tmp/1.mp3", 'wb')
f.write(remotefile.read())
f.close()

