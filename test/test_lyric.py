# -*- coding: utf-8 -*-

'''
Created on Mar 23, 2010

@author: ivan
'''
#from lyr import get_lyrics
#print get_lyrics(u"Ария", u"Я Свободен")
import commands
res = commands.getoutput('ps -a | grep foobnix')
print "b"+res + "a"
if str(res):    
    print "Can't  run, process exists"
    print res
else:
    print "NO processes foobnix in the memory"
    
    
