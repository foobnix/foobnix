# -*- coding: utf-8 -*-

'''
Created on Mar 23, 2010

@author: ivan
'''
#from lyr import get_lyrics
#print get_lyrics(u"Ария", u"Я Свободен")
import commands
import datetime
res = commands.getoutput('ps -a | grep foobnix')
print "b"+res + "a"
if str(res):    
    print "Can't  run, process exists"
    print res
else:
    print "NO processes foobnix in the memory"
    
st = str("16 Mar 1995, 00:00") 
dt= datetime.datetime.strptime(st,"%d %b %Y, %H:%M")
print dt.year

if st:
    i = st.find(",")
    print i
    print st[i-4:i]

