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
    if os.name == 'nt':
        gettext.install(APP_NAME, localedir="share/locale")
    else:
        gettext.install(APP_NAME, unicode=True)
        
    gettext.textdomain(APP_NAME)
    
     

