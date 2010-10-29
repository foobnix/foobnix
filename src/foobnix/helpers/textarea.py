'''
Created on Oct 29, 2010

@author: ivan
'''
import gtk
import gobject
class TextArea(gtk.ScrolledWindow):
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        
        self.buffer = gtk.TextBuffer()

        text = gtk.TextView(self.buffer)
        text.set_editable(False)
        
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(text)

    def set_text(self, text):
        if text:
            gobject.idle_add(self.buffer.set_text, text)