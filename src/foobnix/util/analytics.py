'''
Created on Nov 27, 2012

@author: iivanenko
'''

import urllib
import logging
import urllib2

from foobnix.fc.fc_base import FCBase
from foobnix.util.const import SITE_LOCALE
from foobnix.version import FOOBNIX_VERSION

"""
https://developers.google.com/analytics/devguides/collection/protocol/v1/devguide
https://developers.google.com/analytics/devguides/collection/protocol/v1/reference
https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters

"""

api_url = "http://www.google-analytics.com/collect" 

""" User Open or user Some Feature"""
def action(event_type="unknown"):
    params = {"v":"1",
              "tid":"UA-36625986-1",
               "cid":FCBase().uuid,
               "ul":SITE_LOCALE,
               "t":"appview", #The type of hit. Must be one of 'pageview', 'appview', 'event', 'transaction', 'item', 'social', 'exception', 'timing'.
               "an":"Foobnix",
               "av":FOOBNIX_VERSION,
               "cd":event_type
              }
    
    enq = urllib.urlencode(params)
    response = urllib2.urlopen(api_url, enq, timeout=7)
    
    logging.debug("action analytics" + enq);
    #print enq    
    #print response.read()

""" User  Start Player """    
def begin_session():
    """ To implement """
    None
    
""" User  Stop Player """    
def end_session():
    """ To implement """
    None   

""" User  Type in  Player """    
def error(error_type=""):
    """ To implement """
    None    
     
if __name__ == '__main__':
    action("Radio")  
