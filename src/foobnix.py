#!/usr/bin/env python
'''
Created on Mar 10, 2010

@author: ivan
'''
import pygst
from foobnix.util import LOG
import sys
from foobnix.util.single_instanse import SingleInstance
pygst.require('0.10')

import pygtk
pygtk.require20()

import gtk
import gobject
from foobnix.application.app_view import AppView
from foobnix.application.app_controller import AppController

if __name__ == "__main__":
    myapp = SingleInstance()    
    if myapp.alreadyrunning():
        print  "player running"
        sys.exit(1)
    else:
        LOG.print_debug_info()
        import foobnix.util.localization
        AppController(AppView())
        gobject.threads_init()  #@UndefinedVariable
        gtk.main()
        LOG.info(_("Success"))
