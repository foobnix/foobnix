'''
Created on Mar 5, 2010

@author: ivan
'''
import gtk
from abc import abstractmethod
class InitGlade():    
    
    __GLADE_FILE = "foobnix/glade/foobnix.glade"    
    
    def __init__(self):
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
        
    def getTopLevel(self, topLevenName):
        return gtk.glade.XML(self.__GLADE_FILE, topLevenName)
            
