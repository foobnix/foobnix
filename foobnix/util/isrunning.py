import sys, os, time, atexit
from signal import SIGTERM 
 
class Daemon:
        """
        A generic daemon class.
        
        Usage: subclass the Daemon class and override the run() method
        """
        def __init__(self, pidfile):
                self.pidfile = pidfile
        
        def daemonize(self):
                """
                do the UNIX double-fork magic, see Stevens' "Advanced 
                Programming in the UNIX Environment" for details (ISBN 0201563177)
                http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
                """
                try: 
                        pid = os.fork() 
                        if pid > 0:
                                # exit first parent
                                pass
                except OSError, e: 
                        sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
                        
        
                # decouple from parent environment
                os.chdir("/") 
                os.setsid() 
                os.umask(0) 
        
                # do second fork
                try: 
                        pid = os.fork() 
                        if pid > 0:
                                # exit from second parent
                                #sys.exit(0)
                                pass 
                except OSError, e: 
                        sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
                         
        
                
                        # write pidfile
                atexit.register(self.delpid)
                pid = str(os.getpid())
                file(self.pidfile, 'w+').write("%s\n" % pid)
        
        def delpid(self):
                os.remove(self.pidfile)
 
        def start(self):
                """
                Start the daemon
                """
                # Check for a pidfile to see if the daemon already runs
                try:
                        pf = file(self.pidfile, 'r')
                        pid = int(pf.read().strip())
                        pf.close()
                        print "running"
                except IOError:
                        pid = None
        
                if pid:
                        message = "pidfile %s already exist. Foobnix already running?\n"
                        sys.stderr.write(message % self.pidfile)
                        print "rutting"
                        return False
                
                # Start the daemon
                self.daemonize()
                #self.run()
                print "OK"
                return True
      
