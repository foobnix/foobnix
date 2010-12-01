#!/usr/bin/env python
import sys
from foobnix.regui.controls.dbus_manager import foobnix_dbus_interface
import time
from foobnix.util import LOG

if "test" in sys.argv:
    from test.all import run_all_tests
    print """TEST MODE"""
    result = run_all_tests(ignore="test_core")
    if not result:        
        raise SystemExit("Test failures are listed above.")

init_time = time.time()
iface = foobnix_dbus_interface()

if "debug" in sys.argv:
    LOG.set_logger_level("debug")
    LOG.print_platform_info()
    
if "debug" in sys.argv or not iface:
    print "start server"

    from foobnix.regui.foobnix_core import FoobnixCore
    import gobject
    import gtk

    
    gobject.threads_init() #@UndefinedVariable
    core = FoobnixCore()
    core.dbus.parse_arguments(sys.argv)

    print "******Foobnix run in", time.time() - init_time, " seconds******"
    gtk.main()

else:
    print "client", sys.argv
    print iface.parse_arguments(sys.argv)
