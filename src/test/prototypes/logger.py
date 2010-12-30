#-*- coding: utf-8 -*-
'''
Created on 25 дек. 2010

@author: ivan
'''
import logging

LEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}


#level = LEVELS.get(logging.DEBUG, logging.NOTSET)
logging.basicConfig(level=logging.DEBUG)

logging.debug('This is a debug message')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical error message')
