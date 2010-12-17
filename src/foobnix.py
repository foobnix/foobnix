#!/usr/bin/env python
import sys
from foobnix.regui.controls.dbus_manager import foobnix_dbus_interface
import time
from foobnix.util import LOG
import gobject
from foobnix.regui.foobnix_core import FoobnixCore
import gtk
gobject.threads_init() #@UndefinedVariable
core = FoobnixCore()
core.run()
gtk.main()
gtk.gdk.threads_leave() 