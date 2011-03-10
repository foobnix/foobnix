#-*- coding: utf-8 -*-
'''
Created on 24  2010

@author: ivan
'''
import gettext
import locale
import os

def foobnix_localization():
    APP_NAME = "foobnix"
    gettext.textdomain(APP_NAME)
    gettext.install(APP_NAME, unicode=True)
    
    if os.name == 'nt':
        try:
            lang = gettext.translation(APP_NAME, "share\locale", languages=[locale.getdefaultlocale()[0]])
            lang.install(unicode=True)
        except:
            pass
    
        
    
    
     

