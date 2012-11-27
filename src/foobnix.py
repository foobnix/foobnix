#!/usr/bin/env python

import os
import sys
import gtk
import time
import gobject

from threading import Timer
from foobnix.fc.fc import FC
from foobnix.util import LOG, analytics
from foobnix.fc.fc_helper import CONFIG_DIR


def foobnix():

    if "--debug" in sys.argv:
        for param in sys.argv:
            if param.startswith("--log"):
                if "=" in param:
                    filepath = param[param.index("=")+1 : ]
                    if filepath.startswith('~'):
                        filepath = os.path.expanduser("~") + filepath[1 : ]
                else:
                    filepath = os.path.join(CONFIG_DIR, "foobnix.log")
                LOG.setup("debug", filename=filepath)
        else:
            LOG.setup("debug")
        LOG.print_platform_info()
    else:
        LOG.setup("error")
  
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
        gobject.threads_init() #@UndefinedVariable
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
            gobject.threads_init()    #@UndefinedVariable
            core = FoobnixCore(True)
            core.run()
            #core.dbus.parse_arguments(sys.argv)
            print ("******Foobnix run in", time.time() - init_time, " seconds******")
            if sys.argv:
                Timer(1, gobject.idle_add, [core.check_for_media, sys.argv]).start()
            else:
                analytics.action("Start")
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
