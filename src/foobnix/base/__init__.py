'''
Created on Apr 19, 2010

@author: matik
'''

from gobject import GObject, type_register, signal_new      #@UnresolvedImport
import gobject

SIGNAL_RUN_FIRST = gobject.SIGNAL_RUN_FIRST     #@UndefinedVariable
TYPE_NONE = gobject.TYPE_NONE

class BaseController(GObject):
    
    def __init__(self):
        self.__gobject_init__()
        type_register(self.__class__)
        