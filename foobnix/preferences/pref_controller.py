'''
Created on Mar 14, 2010

@author: ivan
'''
from foobnix.base import BaseController

class PrefController(BaseController):

    def __init__(self, gx_preferences_window):
        self.pref = gx_preferences_window.get_widget("window")
        self.pref.connect("delete-event", self.hide)

    def show(self, sender):
        self.pref.show()

    def hide(self, *args):
        self.pref.hide()
        return True
