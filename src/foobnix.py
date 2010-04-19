#!/usr/bin/env python
'''
Created on Mar 10, 2010

@author: ivan
'''
import pygst
pygst.require('0.10')

import pygtk
pygtk.require20()

import gtk
import gettext
from foobnix.application.app_view import AppView
from foobnix.application.app_controller import AppController

if __name__ == "__main__":
    APP_NAME = "foobnix"
    gettext.install(APP_NAME, unicode=True)
    gettext.textdomain(APP_NAME)
    gtk.glade.textdomain(APP_NAME)
    
    AppController(AppView())
    gtk.gdk.threads_init()  #@UndefinedVariable
    gtk.main()
    print _("Success")
