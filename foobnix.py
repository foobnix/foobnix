#!/usr/bin/env python
'''
Created on Mar 10, 2010

@author: ivan
'''
import pygst
from foobnix.util import LOG
pygst.require('0.10')

import pygtk
pygtk.require20()

import gtk
import gobject
import gettext
from foobnix.application.app_view import AppView
from foobnix.application.app_controller import AppController
import __main__, os

def is_only_instance():
    # Determine if there are more than the current instance of the application
    # running at the current time.
    return os.system("(( $(ps -ef | grep python | grep '[" + 
                     __main__.__file__[0] + "]" + __main__.__file__[1:] + 
                     "' | wc -l) > 1 ))") != 0

if __name__ == "__main__":
    LOG.print_debug_info()
    if is_only_instance():        
        APP_NAME = "foobnix"
        gettext.install(APP_NAME, unicode=True)
        gettext.textdomain(APP_NAME)
        gtk.glade.textdomain(APP_NAME)
        
        AppController(AppView())
        
        gobject.threads_init()  #@UndefinedVariable
        gtk.main()
            
        LOG.info(_("Success"))
    else:
        LOG.warn("Other instance of player is already running")
