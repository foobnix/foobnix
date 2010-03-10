'''
Created on Mar 9, 2010

@author: ivan
'''
from deluge.log import LOG
class BusController():
    def __init__(self):
        self._mainWindowWidget = None
        self._playerEngine = None
    
    def setSeek(self, persent):
        if self._playerEngine:
            self._playerEngine.seek(persent);
        else:
            LOG.debug("Player Engine is not registered")
        
    def setMainWindowWidget(self, widget):
        self._mainWindowWidget = widget
    
    def setPlayerEngine(self, engine):
        self._playerEngine = engine
        