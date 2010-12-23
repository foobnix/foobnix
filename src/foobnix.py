#!/usr/bin/env python
import sys
import time
from foobnix.regui.foobnix_core import FoobnixCore
import gtk
import os
import gobject
import logging


if "test" in sys.argv:
    from test.all import run_all_tests
    print """TEST MODE"""
    result = run_all_tests(ignore="test_core")
    if not result:        
        raise SystemExit("Test failures are listed above.")

def other():
    print "start server other"
    init_time = time.time()
    gobject.threads_init() 
    core = FoobnixCore()
    core.run()    
    print "******Foobnix run in", time.time() - init_time, " seconds******"
    gtk.main()

def gnome():
    init_time = time.time()
    from foobnix.regui.controls.dbus_manager import foobnix_dbus_interface
    iface = foobnix_dbus_interface()
    
    if "debug" in sys.argv:
        logging.basicConfig(level=logging.INFO)


    if "debug" in sys.argv or not iface:
        print "start server gnome"
        gobject.threads_init()
        core = FoobnixCore()
        core.run()
        core.dbus.parse_arguments(sys.argv)
        print "******Foobnix run in", time.time() - init_time, " seconds******"
        gtk.main()
    
    else:
        print "client", sys.argv
        print iface.parse_arguments(sys.argv)

if 'gnome' == os.environ.get('DESKTOP_SESSION'):
    gnome()
else:
    other()
