#!/usr/bin/env python
'''
Created on Mar 10, 2010

@author: ivan
'''
import gobject
import gtk
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import sys
import time
import os
class Manager(dbus.service.Object):
    def __init__(self, interface, object_path='/org/foobnix_player/FoobnixObject'):
        self.interface = interface
        self.bus = dbus.SessionBus()
        bus_name = dbus.service.BusName("org.foobnix_player.Foobnix", bus=self.bus)
        dbus.service.Object.__init__(self, bus_name, object_path)

    @dbus.service.method('org.foobnix_player.Foobnix')
    def interactive_play_args(self, args):
        print "manager recive", args
        self.interface.play_args(args)
        
def on_mediakey(comes_from, what):
    """
    gets called when multimedia keys are pressed down.
    """
    if what in ['Stop', 'Play', 'Next', 'Previous']:
        if what == 'Stop':
            os.system('foobnix --stop')
        elif what == 'Play':
            os.system('foobnix --play')
        elif what == 'Next':
            os.system('foobnix --next')
        elif what == 'Previous':
            os.system('foobnix --prev')
    else:
        print ('Got a multimedia key...')
        

class Foobnix():
    def __init__(self):
        from foobnix.application.app_view import AppView
        from foobnix.application.app_controller import AppController
        import foobnix.util.localization
        Manager(self)       
        self.app = AppController(AppView())
    
    def start(self):
        gobject.threads_init()
        gtk.gdk.threads_enter()
        gtk.main()    
        
    def play_args(self, args):
        list = eval(args)
        print "fobonix play",
        for i in list:
            print i 
        self.app.play_arguments(list)  

init_time = time.time()

DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()
dbus_objects = dbus.Interface(bus.get_object('org.freedesktop.DBus', '/org/freedesktop/DBus'), 'org.freedesktop.DBus').ListNames()


if not "org.foobnix_player.Foobnix" in dbus_objects:
    print "start server"    
    foobnix = Foobnix()
    print "******Foobnix run in", time.time() - init_time, " seconds******"
    foobnix.start()
    
else:
    print "start client"    
    proxy = bus.get_object('org.foobnix_player.Foobnix', '/org/foobnix_player/FoobnixObject')    
    iface = dbus.Interface(proxy, 'org.foobnix_player.Foobnix')
    
    dbus_interface = 'org.gnome.SettingsDaemon.MediaKeys'
    mm_object = bus.get_object('org.gnome.SettingsDaemon', '/org/gnome/SettingsDaemon/MediaKeys')
    mm_object.GrabMediaPlayerKeys("MyMultimediaThingy", 0, dbus_interface=dbus_interface)
    mm_object.connect_to_signal('MediaPlayerKeyPressed', on_mediakey)

    if sys.argv:
        iface.interactive_play_args(str(sys.argv))

