'''
Created on Mar 14, 2010

@author: ivan
'''
class PrefController():
    def __init__(self, gxPref):
        self.gxPref = gxPref
        self.pref =  gxPref.get_widget("window")        
        self.pref.connect("delete-event", self.hide)
    
    def show(self):
        print "show"        
        self.pref.show()
        
    def hide(self, *args):
        print "hide"
        self.pref.hide()
        return True
        
        
    