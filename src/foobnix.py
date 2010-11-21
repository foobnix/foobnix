#!/usr/bin/env python

import sys

if sys.argv and "debug" in sys.argv:
    from test.all import run_all_tests
    print """DEBUG MODE"""
    result = run_all_tests(ignore="test_core")
    if not result:        
        raise SystemExit("Test failures are listed above.")

from foobnix.regui.controls.dbus_manager import foobnix_dbus_interface
from foobnix.regui.foobnix_core import FoobnixCore
import time
import gobject
import gtk

init_time = time.time()
iface = foobnix_dbus_interface()
if not iface:
    print "start server"
    
    gobject.threads_init() #@UndefinedVariable
    core = FoobnixCore()
    core.dbus.parse_arguments(sys.argv)

    print "******Foobnix run in", time.time() - init_time, " seconds******"
    gtk.main()


else:
    print "start client"
    iface.parse_arguments(sys.argv)
