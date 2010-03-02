from threading import Lock, Thread
import threading
import time

class Some:
    def __init__(self):
        self.i = 1 

    def counter(self):
        self.i += 1
        print self.i

class MyThread(threading.Thread):
    def run(self):
        while True:
            print "a"

lock = Lock()            
def myfunc(thread_id):
    lock.acquire()    
    print "run " + thread_id
    time.sleep(1)
    print "end" + thread_id
    lock.release()
for i in xrange(10):
    t = Thread(target=myfunc, args=(str(i)))
    t.start()
            


