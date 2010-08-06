'''
Created on Jul 27, 2010

@author: ivan
'''
import os
import ConfigParser
from foobnix.util import LOG
from foobnix.util.singleton import Singleton

        
class Config:
    __metaclass__ = Singleton
    FOOBNIX = "foobnix"
    SUPPORTED_AUDIO_FORMATS = 'supported_audio_formats'
    
    USER_DIR = os.getenv("HOME") or os.getenv('USERPROFILE')
    CFG_LOCAL_FILE = USER_DIR + "/foobnix.cfg"
    CFG_INSTALLED_FILE = USER_DIR + "/foobnix.cfg"
    CFG_LOCAL_TEST_FILE = "../../foobnix.cfg"
     
    def __init__(self):
        self.config = None
        
        if self.get_file_path():
            self.config = ConfigParser.RawConfigParser()
            self.config.read(self.get_file_path())
        else:
            LOG.error("Config file not found")
        
    def get_file_path(self):
       
        if os.path.isfile(self.CFG_LOCAL_FILE):
            LOG.debug("Read local cfg file", self.CFG_LOCAL_FILE)
            return self.CFG_LOCAL_FILE
        elif os.path.isfile(self.CFG_INSTALLED_FILE):
            LOG.debug("Read installed cfg file", self.CFG_INSTALLED_FILE)
            return self.CFG_INSTALLED_FILE
        elif os.path.isfile(self.CFG_LOCAL_TEST_FILE):
            LOG.debug("Read local cfg file from test", self.CFG_LOCAL_TEST_FILE)
            return self.CFG_LOCAL_TEST_FILE
        else:
            LOG.debug("Config file not found")
            return None
            
    
    def get(self, type):
        if self.config:
            LOG.debug("Get cfg value for", type)
            return self.config.get(self.FOOBNIX, type)
        else:
            return None

def test():
    print Config().get(Config.SUPPORTED_AUDIO_FORMATS)
    print Config().get(Config.SUPPORTED_AUDIO_FORMATS)
    print Config().get(Config.SUPPORTED_AUDIO_FORMATS)
    
    
test()    
