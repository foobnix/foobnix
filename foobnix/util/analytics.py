'''
Created on Nov 27, 2012

@author: iivanenko
'''

import urllib
import urllib.parse
import urllib.request
import logging
import platform
import threading

from foobnix.version import FOOBNIX_VERSION
from foobnix.fc.fc_base import FCBase
from foobnix.util.const import SITE_LOCALE



"""
https://developers.google.com/analytics/devguides/collection/protocol/v1/devguide
https://developers.google.com/analytics/devguides/collection/protocol/v1/reference
https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters
"""

api_url = "http://www.google-analytics.com/collect" 


def send(d={"t":"appview"}):
    params = { 
               "v":"1",
               "tid":"UA-36625986-1",
               "cid":FCBase().uuid,
                "ul":SITE_LOCALE,
                "an":"Foobnix",
                "av":FOOBNIX_VERSION,
                "cd1":platform.python_version(),
                "cd2":platform.platform()
              }
    params.update(d)

    #logging.debug("analytics params: "+str(params));
    enq = urllib.parse.urlencode(params).encode("utf-8")
    threading.Thread(target=urllib.request.urlopen, args=(api_url, enq)).start()
    

""" User Open or user Some Feature"""
def action(event_type="unknown"):
    send(d={"t":"appview","cd":event_type})
    logging.debug("analytics: action "+event_type);

""" User  Start Player """    
def begin_session():
    send(d={"t":"appview","sc":"start"})
    logging.debug("analytics: begin_session");
    
""" User  Stop Player """    
def end_session():
    send(d={"t":"appview","sc":"end"})
    logging.debug("analytics: end_session");

""" User  Type in  Player """    
def error(exDescription="Error"):
    send(d={"t":"exception","exd":exDescription})
    logging.debug("analytics: error");
     
if __name__ == '__main__':
    begin_session()
    action("Radio")  
    error("MainCrash")
    end_session()
