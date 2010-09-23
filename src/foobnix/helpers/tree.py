'''
Created on Sep 23, 2010

@author: ivan
'''
import gtk
class ScrolledTreeView(gtk.TreeView):
    def __init__(self, policy_horizontal, policy_vertical):
        gtk.TreeView.__init__(self)
        scrool = gtk.ScrolledWindow()        
        scrool.set_policy(policy_horizontal, policy_vertical)
        scrool.add_with_viewport(self)
        scrool.show_all()
        
        self.scroll = scrool
        self.tree = self
    
        