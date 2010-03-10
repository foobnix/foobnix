'''
Created on Mar 5, 2010

@author: ivan
'''
class WindowService():
    def __init__(self, widget):
        self._widget = widget
        self._isVisible = True
    
    def isVisible(self):
        return self._isVisible
    
    def setVisible(self, bool):
        self._isVisible = bool       
        
    def show(self):
        self._widget.show()
    
    def hide(self):
        self._widget.hide()