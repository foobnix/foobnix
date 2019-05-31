#!/usr/bin/env python

import gi
import os
import sys
import time
import logging
import traceback

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
from gi.repository import GLib

from threading import Timer
from foobnix.fc.fc import FC
from foobnix.util import LOG, analytics
from foobnix.fc.fc_helper import CONFIG_DIR


def except_hook(exc_t, exc_v, traceback):
    logging.error("*** Uncaught exception ***")
    logging.error(exc_t)
    logging.error(exc_v)
    logging.error(traceback)

#sys.excepthook = except_hook

def foobnix():

    if "--debug" in sys.argv:
        LOG.with_print = True
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

    from foobnix.gui.foobnix_core import FoobnixCore

    if "--test" in sys.argv:
        from test.all import run_all_tests
        print("""TEST MODE""")
        result = run_all_tests(ignore="test_core")
        if not result:
            raise SystemExit("Test failures are listed above.")
        exit()

    init_time = time.time()

    if "--nt" in sys.argv or os.name == 'nt':
        core = FoobnixCore(False)
        core.run()
        analytics.begin_session()
        print("******Foobnix run in", time.time() - init_time, " seconds******")
        Gtk.main()
    else:
        init_time = time.time()
        from foobnix.gui.controls.dbus_manager import foobnix_dbus_interface
        iface = foobnix_dbus_interface()
        if "--debug" in sys.argv or not iface:
            print("start program")
            core = FoobnixCore(True)
            core.run()
            analytics.begin_session()
            #core.dbus.parse_arguments(sys.argv)
            analytics.begin_session()
            print("******Foobnix run in", time.time() - init_time, " seconds******")
            if sys.argv:
                Timer(1, GLib.idle_add, [core.check_for_media, sys.argv]).start()

            Gtk.main()
        else:
            print(iface.parse_arguments(sys.argv))

if "--profile" in sys.argv:
    import cProfile
    cProfile.run('foobnix()')
else:
    try:
        foobnix()
        analytics.end_session()
    except Exception as e:
        analytics.end_session()
        analytics.error("Main Exception"+str(e))
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        FC().save()
