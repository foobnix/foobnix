'''
Created on Mar 5, 2010

@author: ivan
'''
import gtk.glade

class InitGlade():    
    
    __GLADE_FILE = "foobnix/glade/foobnix.glade"    
    
    def __init__(self, topLelenName = None):
        self._topLevelName = topLelenName
        customStyles = ''' 
            style "menubar-style" { 
                GtkMenuBar::shadow_type = none
                GtkMenuBar::internal-padding = 0                                 
                }                         
             class "GtkMenuBar" style "menubar-style"
        '''
        gtk.rc_parse_string(customStyles)
        
    def getGladeFile(self):        
        return self.__GLADE_FILE
        
    def getTopLevel(self, topLevenName=None):
        if topLevenName:
            return gtk.glade.XML(self.__GLADE_FILE, topLevenName)
        else:
            return gtk.glade.XML(self.__GLADE_FILE, self._topLevelName)

    