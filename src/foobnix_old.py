#!/usr/bin/env python
'''
Created on Mar 10, 2010

@author: ivan
'''
import gobject
import gtk
from foobnix.util.dbus_utils import DBusManager, getFoobnixDBusInterface
import sys
import time
import os
import thread

class Foobnix():
    def __init__(self):
        from foobnix.application.app_view import AppView
        from foobnix.application.app_controller import AppController
        import foobnix.util.localization
        self.dbus = DBusManager(self)
        self.app = AppController(AppView())

    def start(self):
        gobject.threads_init()
        gtk.gdk.threads_enter()
        gtk.main()

    def play_args(self, args):
        arg_list = eval(args)
        print "fobonix play",
        for i in arg_list:
            print i
        self.app.play_arguments(arg_list)

init_time = time.time()

iface = getFoobnixDBusInterface()

if not iface:
    print "start server"
    foobnix = Foobnix()
    print "******Foobnix run in", time.time() - init_time, " seconds******"
    foobnix.start()

else:
    print "start client"
    if sys.argv:
        iface.interactive_play_args(str(sys.argv))

