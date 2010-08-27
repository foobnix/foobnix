#!/usr/bin/env python
'''
Created on Mar 10, 2010

@author: ivan
'''
import Pyro.core
import sys
import thread

class FobonixServer(Pyro.core.ObjBase):
            def __init__(self, app):
                Pyro.core.ObjBase.__init__(self)
                self.app = app
                    
            
            def test(self):
                print "TEST SUCCESS"
                return True
            
            def commands(self,args):
                print "SERVER COMMANDS"
                if self.app:
                    print "SERVER COMMANDS ARGUMENTS"
                    self.app.play_arguments(args)            
                    
                
            def play(self, song):
                print song

class Foobnix():
    def __init__(self):       
        self.app = None
        client = self.client()
        if client:
            print "Client, acept commands"
            try:
                client.commands(sys.argv)
            except:
                print >> sys.stderr, "ERROR", "Pyro.errors.ConnectionClosedError: connection lost"
            
        else:   
                       
            from foobnix.application.app_view import AppView
            from foobnix.application.app_controller import AppController
            import gobject
            import gtk
            
            import foobnix.util.localization
            app = AppController(AppView())
            thread.start_new_thread(self.server,(app,))
            
            gobject.threads_init()  #@UndefinedVariable
            gtk.main()
            
    
    def client(self):
        try:
            client = Pyro.core.getProxyForURI("PYROLOC://localhost:7766/foobnix")
            client.test()
            print "run client"
            return client
        except:
            print "client exeption"            
            return None        
        
    def server(self,app):
        print "run server"
        Pyro.core.initServer()
        daemon=Pyro.core.Daemon()
        uri=daemon.connect(FobonixServer(app),"foobnix")
        
        print "The daemon runs on port:",daemon.port
        print "The object's uri is:",uri
        
        daemon.requestLoop(timeout=10)
                
                
if __name__ == "__main__":
    foobnix = Foobnix();
    