#!/usr/bin/env python
import sys
import time
import gtk
import gobject
import os
from foobnix.util import LOG
from foobnix.fc.fc import FC

def foobnix():
    if "--debug" in sys.argv:
        LOG.setup("debug")
        LOG.print_platform_info()
    else:
        LOG.setup("error")
        #LOG.setup("debug")
    
    from foobnix.regui.foobnix_core import FoobnixCore
    
    if "--test" in sys.argv:
        from test.all import run_all_tests
        print ("""TEST MODE""")
        result = run_all_tests(ignore="test_core")
        if not result:        
            raise SystemExit("Test failures are listed above.")
        exit()
    
    init_time = time.time()
    
    if "--nt" in sys.argv or os.name == 'nt':    
        gobject.threads_init()
        core = FoobnixCore(False)
        core.run()
        print ("******Foobnix run in", time.time() - init_time, " seconds******")
        gtk.main()
    else:
        init_time = time.time() 
        from foobnix.regui.controls.dbus_manager import foobnix_dbus_interface
        iface = foobnix_dbus_interface()
        if "--debug" in sys.argv or not iface:
            print ("start program")
            gobject.threads_init()    
            core = FoobnixCore(True)
            core.run()
            core.dbus.parse_arguments(sys.argv)
            print ("******Foobnix run in", time.time() - init_time, " seconds******")
            gtk.main()
    
        else:
            print (iface.parse_arguments(sys.argv))

if "--profile" in sys.argv:
    import cProfile
    cProfile.run('foobnix()')
else:    
    try:
        foobnix()
    except Exception, e:
        print e
        FC().save()
    
