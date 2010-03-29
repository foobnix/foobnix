'''
Created on Mar 13, 2010

@author: ivan
'''
import gtk
class WindowController():
    def __init__(self, gxMain, gxAbout,  prefCntr):
        self.decorate(gxMain)
        self.prefCntr = prefCntr
        
        
          
        self.window = gxMain.get_widget("foobnixWindow")
        self.window.maximize()
        #self.window.connect("destroy", self.onDestroy)
        self.window.connect("delete-event", self.hide)
    
        self.window.set_title("Foobnix 1.0 beta")
        
        signalsPopup = {
                "on_gtk-preferences_activate" :self.showPref,
                "on_file_quit_activate":self.onDestroy,
                "on_menu_about_activate":self.showAbout               
        }
        
        gxMain.signal_autoconnect(signalsPopup)     
        
        self.about = gxAbout.get_widget("aboutdialog")
        self.about.connect("delete-event", self.hideAbout)
         
        
    def showAbout(self, *args):
        self.about.show()
    def hideAbout(self, *args):
        self.about.hide()
        return True
    
    def showPref(self, *args):
        self.prefCntr.show()
        
        
    def setTitle(self, text):
        self.window.set_title(text)
    
    def registerOnExitCnrt(self, onExitCnrt):
        self.onExitCnrt = onExitCnrt
    
    def show(self):
        self.window.show()
    
    def hide(self, *args):
        self.window.hide()
        return True
    
    def onDestroy(self, *a):
        print "Destroy"        
        self.onExitCnrt.onExit()
        gtk.main_quit() 
        
        
    def decorate(self, gx):
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
        
