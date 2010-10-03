'''
Created on Sep 30, 2010

@author: ivan
'''
import time
from foobnix.regui.controls.dbus_manager import foobnixDBusInterface

init_time = time.time()

iface = foobnixDBusInterface()

if not iface:
    print "start server"
    import gobject
    from foobnix.regui.foobnix_core import FoobnixCore
    import gtk
    gobject.threads_init() #@UndefinedVariable
    #gtk.gdk.threads_enter()
    eq = FoobnixCore()
    print "******Foobnix run in", time.time() - init_time, " seconds******"
    gtk.main()
else:
    print "start client"
    