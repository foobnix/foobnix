'''
Created on Feb 26, 2010

@author: ivan
'''

import sys

def debug(*args):
    print "DEBUG:", args

def info(*args):    
    print "INFO:", args

def warn(*args):    
    print "WARN:", args    

def error(*args):    
    print >> sys.stderr, args
    