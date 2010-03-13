'''
Created on Mar 13, 2010

@author: ivan
'''
import gtk
class WindowController():
    def __init__(self, gx):
        self.window = gx.get_widget("foobnixWindow")
        self.window.connect("destroy", self.onDestroy)
    
    def registerOnExitCnrt(self, onExitCnrt):
        self.onExitCnrt = onExitCnrt
    
    def show(self):
        self.window.show()
    
    def hide(self):
        self.window.hide()
    
    def onDestroy(self, *a):
        print "Destroy"
        self.onExitCnrt.onExit()
        gtk.main_quit() 