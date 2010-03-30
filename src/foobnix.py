#!/usr/bin/env python
'''
Created on Mar 10, 2010

@author: ivan
'''
from foobnix.application.app_view import AppView
from foobnix.application.app_controller import AppController
import os
import gtk
import gettext

gettext.install('foobnix', unicode=True)
gettext.textdomain('foobnix')
    
class App():
    def __init__(self):
        v = AppView()  
        AppController(v)
    
if __name__ == "__main__":
    app = App()
    gtk.gdk.threads_init() #@UndefinedVariable
    gtk.main()    
    print _("Success")
    
