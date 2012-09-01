'''
Created on Oct 29, 2010

@author: ivan
'''

import gtk
import pango
import gobject

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
        gobject.idle_add(self.buffer.insert_pixbuf, enditer, image.get_pixbuf())
        
    def set_text(self, text="", bold_text=""):
        def safe_task():
            full_text = bold_text + "\n" + text + "\n"
            self.buffer.set_text(full_text)
            if text:
                self.clear_tags (full_text)
            start = self.buffer.get_iter_at_offset(0)            
            end = self.buffer.get_iter_at_offset(len(unicode(bold_text)))
            self.buffer.apply_tag(self.tag_bold, start, end)
        gobject.idle_add(safe_task)
        
    def clear_tags (self, text):
        start_index = 0
        text_length = len(text)
        while (start_index != -1):
            buf_text = self.buffer.get_text(self.buffer.get_iter_at_offset(0),
                                        self.buffer.get_iter_at_offset(text_length))
            start_index = buf_text.find ("<")
            if start_index != -1:
                end_index = buf_text.find (">", start_index)
                if end_index != -1:
                    start = self.buffer.get_iter_at_offset(start_index)
                    end = self.buffer.get_iter_at_offset(end_index + 1) 
                    self.buffer.delete(start, end)
                                        
class ScrolledText():
    def __init__(self):
        self.buffer = gtk.TextBuffer()
        self.text = gtk.TextView(self.buffer)
        self.text.set_editable(False)
        self.text.set_cursor_visible(False)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self.text)     
