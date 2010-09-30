'''
Created on Sep 30, 2010

@author: ivan
'''
import time
import gobject
from foobnix.regui.foobnix_core import FoobnixCore
import gtk
init_time = time.time()
gobject.threads_init() #@UndefinedVariable
#gtk.gdk.threads_enter()
eq = FoobnixCore()
print "******Foobnix run in", time.time() - init_time, " seconds******"
gtk.main()