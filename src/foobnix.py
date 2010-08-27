#!/usr/bin/env python
'''
Created on Mar 10, 2010

@author: ivan
'''

import Pyro.core
import gobject
import threading
import sys
#http://code.google.com/p/media-enclave/source/browse/trunk/aenclave/gst_player/gst_server.py?spec=svn200&r=111
class Foobnix():
    def __init__(self):
        from foobnix.application.app_view import AppView
        from foobnix.application.app_controller import AppController
        import foobnix.util.localization
        import sys
               
        self.app = AppController(AppView())
        
    def play_args(self, args):
        self.app.play_arguments(args)  
        
class RemotePlayer(Pyro.core.ObjBase):
    """
    A Pyro remote object that wraps a GstPlayer.
    """
    def __init__(self):        
        Pyro.core.ObjBase.__init__(self)
        self.foo = Foobnix()
        

    def check(self):
        return True
    def play_args(self, args):
        self.foo.play_args(args)
    
def client():
    client = Pyro.core.getProxyForURI("PYROLOC://localhost:7766/foobnix")
    try:
        client.check()
        return client
    except:
        return None

def main():
    cl = client()
    if cl:
        print sys.argv
        if sys.argv and len(sys.argv) > 1: 
            cl.play_args(sys.argv)
        print "Player running"
        return None
    
    # Setup the Pyro daemon.
    Pyro.config.PYRO_TRACELEVEL = 3
    Pyro.config.PYRO_STDLOGGING = True
    Pyro.core.initServer()
    daemon = Pyro.core.Daemon()
    # Create the player and register it with the Pyro name server.
    player = RemotePlayer()
    # TODO(rnk): Change the naming to make one remote object per channel.
    uri = daemon.connect(player, "foobnix")
    print "The object URI: %s" % uri
    # Run the event loop in another daemon thread.  Marking it as a daemon
    # allows us to respond to SIGTERM properly.
    gobject.threads_init()
      
    event_thread = threading.Thread(target=gobject.MainLoop().run)
    event_thread.setDaemon(True)  # TODO(rnk): For 2.6+ switch to the below.
    #event_thread.daemon = True
    event_thread.start()    
    # Run the Pyro request loop.
    try:
        daemon.requestLoop()
        
    finally:
        print "exiting main thread"
        daemon.shutdown()

if __name__ == "__main__":
    main()

