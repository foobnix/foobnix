'''
Created on Mar 21, 2010

@author: ivan
'''
import time
import thread

class DemoThread:
    def __init__(self):
        self.result = 0
        
        self.playerThreadId = thread.start_new_thread(self.calc, (10,))
        
        print "RESULT", self.result
        time.sleep(3)
        print "RESULT", self.result

    def calc(self,num):
        print num
        for i in xrange(num):
            self.result += i 
            time.sleep(0.1)
            
demo = DemoThread()            
            
    
