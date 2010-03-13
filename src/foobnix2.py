'''
Created on Mar 10, 2010

@author: ivan
'''

import gtk.glade
from foobnix.application.app_view import AppView
from foobnix.application.app_controller import AppController

class App():
    def __init__(self):        
        v = AppView()  
        c = AppController(v)
        pass
        
    pass # end of class


if __name__ == "__main__":
    app = App()
    gtk.gdk.threads_init() #@UndefinedVariable
    gtk.main()
    print "Succes"