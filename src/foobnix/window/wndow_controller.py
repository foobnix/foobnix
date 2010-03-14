'''
Created on Mar 13, 2010

@author: ivan
'''
import gtk
class WindowController():
    def __init__(self, gx):
        self.decorate(gx)
          
        self.window = gx.get_widget("foobnixWindow")
        self.window.maximize()
        self.window.connect("destroy", self.onDestroy)
    
        self.window.set_title("Foobnix 1.0 beta")
        
    def setTitle(self, text):
        self.window.set_title(text)
    
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
        
        
    def decorate(self,gx):
        rc_st = ''' 
                        style "menubar-style" { 
                            GtkMenuBar::shadow_type = none
                            GtkMenuBar::internal-padding = 0                                 
                            }                         
                         class "GtkMenuBar" style "menubar-style"
                    '''
            
        gtk.rc_parse_string(rc_st)         
        
        
        menuBar = gx.get_widget("menubar3")
        labelColor = gx.get_widget("label31")
        bgColor = labelColor.get_style().bg[gtk.STATE_NORMAL]
        txtColor = labelColor.get_style().fg[gtk.STATE_NORMAL]
        
        
        menuBar.modify_bg(gtk.STATE_NORMAL, bgColor)
        
        items = menuBar.get_children()
        
        #Set god style for main menu
        for item in items:
            current = item.get_children()[0]                
            current.modify_fg(gtk.STATE_NORMAL, txtColor)    
        