#!/usr/bin/env python
'''
Created on Sep 30, 2010

@author: ivan
'''

import time
import sys
from foobnix.regui.controls.dbus_manager import foobnixDBusInterface
import gobject

DEBUG_MODE = True

iface = foobnixDBusInterface()

if DEBUG_MODE:
    from test.all import run_all_tests
    """DEBUG MODE"""
    result = run_all_tests()
    if not result:        
        raise SystemExit("Test failures are listed above.")

init_time = time.time()
if not iface:
    print "start server"

    from foobnix.regui.foobnix_core import FoobnixCore
    import gtk

    gobject.threads_init()
    #core = FoobnixCore()
    #core.dbus.parse_arguments(sys.argv)

    print "******Foobnix run in", time.time() - init_time, " seconds******"
    gtk.main()


else:
    print "start client"
    iface.parse_arguments(sys.argv)
