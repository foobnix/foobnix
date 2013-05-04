'''
Created on Sep 23, 2010

@author: ivan
'''
from gi.repository import Gtk
class ScrolledTreeView(Gtk.TreeView):
    def __init__(self, policy_horizontal, policy_vertical):
        Gtk.TreeView.__init__(self)
        scrool = Gtk.ScrolledWindow()
        scrool.set_policy(policy_horizontal, policy_vertical)
        scrool.add_with_viewport(self)
        scrool.show_all()
        
        
        
        
        