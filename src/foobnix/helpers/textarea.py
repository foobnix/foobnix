'''
Created on Oct 29, 2010

@author: ivan
'''

import gtk
import pango

from foobnix.helpers.image import ImageBase


class TextArea(gtk.ScrolledWindow):
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        
        texttagtable = gtk.TextTagTable()
        self.buffer = gtk.TextBuffer(texttagtable)
        
        self.tag_bold = gtk.TextTag("bold")
        self.tag_bold.set_property("weight", pango.WEIGHT_BOLD)
        
        texttagtable.add(self.tag_bold)
        
        text = gtk.TextView(self.buffer)
        text.set_wrap_mode(gtk.WRAP_WORD)
        text.set_editable(False)
                
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.add(text)
        
        self.scroll = self
        self.line_title = None
        
    def append_image(self, url):
        if not url:
            return None
        enditer = self.buffer.get_end_iter()
        image = ImageBase(None)
        image.set_image_from_url(url)
        self.buffer.insert_pixbuf(enditer, image.get_pixbuf())
        
    def set_text(self, text="", bold_text=""):
        if not text:
            text = ""

        self.buffer.set_text(bold_text + "\n" + text)
        start = self.buffer.get_iter_at_offset(0)            
        end = self.buffer.get_iter_at_offset(len(bold_text))
        self.buffer.apply_tag(self.tag_bold, start, end)

    
class ScrolledText():
    def __init__(self):
        self.buffer = gtk.TextBuffer()
        self.text = gtk.TextView(self.buffer)
        self.text.set_editable(False)
        self.text.set_cursor_visible(False)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self.text)     
