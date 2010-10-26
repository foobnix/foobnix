#!/usr/bin/env python
'''
Created on Sep 30, 2010

@author: ivan
'''
import time
import sys
from foobnix.regui.controls.dbus_manager import foobnixDBusInterface

init_time = time.time()

iface = foobnixDBusInterface()

if not iface:
    print "start server"
    from foobnix.regui.foobnix_core import FoobnixCore
    import gtk
    gtk.gdk.threads_init()
    eq = FoobnixCore()
    eq.dbus.parse_arguments(sys.argv)
    print "******Foobnix run in", time.time() - init_time, " seconds******"
    gtk.main()
    
else:
    print "start client"
    if sys.argv:
        iface.parse_arguments(sys.argv)

