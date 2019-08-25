#-*- coding: utf-8 -*-
'''
Created on 5 дек. 2010

@author: ivan
'''
def chardecode_crash():
    s = u'\x00Q\x00u\x00i\x00c\x00k'
    print(s)
    print(s == 'Quick')
    import re
    re.search('Quick', s)
    import chardet
    print(chardet.detect(s))
    print(s.decode('utf_16'))
    
    print("Success")

class A():
    def __init__(self):
        print("a")
    
    def go(self):
        print(self.param)
    
class B(A):
    def __init__(self):
        A.__init__(self)
        print("b")
        self.param = "hi"

b = B()
b.go()
