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
    #gettext.install(APP_NAME, unicode=True)
    #gettext.bindtextdomain(APP_NAME, "share/locale")
    #gettext.textdomain(APP_NAME)
     
    l = locale.setlocale(locale.LC_ALL, '')
    os.environ.setdefault('LANG', locale.normalize(l))
    t = gettext.translation(APP_NAME)
    t.install(unicode=True) 
     

