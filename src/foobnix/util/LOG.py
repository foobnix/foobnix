'''
Created on Feb 26, 2010

@author: ivan
'''

import sys
import platform
import logging


def init():
    LOG_FILENAME = '/tmp/foobnix.log'
    LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}
    logging.basicConfig(filename=LOG_FILENAME, level=logging.NOTSET)
    

def debug(*args):
    init()
    print "DEBUG:", args
    logging.debug(args)

def info(*args): 
    init()   
    print "INFO:", args
    logging.info(args)

def warn(*args):
    init()    
    print  "WARN:", args
    logging.warn(args)    

def error(*args):
    init()    
    print >> sys.stderr, "ERROR", args
    logging.error(args)

def print_debug_info():
    init()
    debug('*************** PLATFORM INFORMATION ************************')
    
    debug('==Interpreter==')
    debug('Version      :', platform.python_version())
    debug('Version tuple:', platform.python_version_tuple())
    debug('Compiler     :', platform.python_compiler())
    debug('Build        :', platform.python_build())
    
    debug('==Platform==')
    debug('Normal :', platform.platform())
    debug('Aliased:', platform.platform(aliased=True))
    debug('Terse  :', platform.platform(terse=True))
    
    debug('==Operating System and Hardware Info==')
    debug('uname:', platform.uname())
    debug('system   :', platform.system())
    debug('node     :', platform.node())
    debug('release  :', platform.release())
    debug('version  :', platform.version())
    debug('machine  :', platform.machine())
    debug('processor:', platform.processor())
    
    debug('==Executable Architecture==')
    debug('interpreter:', platform.architecture())
    debug('/bin/ls    :', platform.architecture('/bin/ls'))
    debug('*******************************************************')
    
        
