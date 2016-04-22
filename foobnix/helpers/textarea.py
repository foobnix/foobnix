'''
Created on Oct 29, 2010

@author: ivan
'''

from gi.repository import Pango
from gi.repository import Gtk

from foobnix.helpers.image import ImageBase
from foobnix.util import idle_task


class TextArea(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        texttagtable = Gtk.TextTagTable()
        self.buffer = Gtk.TextBuffer.new(texttagtable)

        self.tag_bold = Gtk.TextTag(name="bold")
        self.tag_bold.set_property("weight", Pango.Weight.BOLD)

        texttagtable.add(self.tag_bold)

        text = Gtk.TextView(buffer=self.buffer)
        text.set_wrap_mode(Gtk.WrapMode.WORD)
        text.set_editable(False)

        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.add(text)

        self.scroll = self
        self.line_title = None

    @idle_task
    def append_image(self, url):
        if not url:
            return None
        enditer = self.buffer.get_end_iter()
        image = ImageBase(None)
        image.set_image_from_url(url)
        self.buffer.insert_pixbuf(enditer, image.get_pixbuf())

    @idle_task
    def set_text(self, text="", bold_text=""):
        if not text:
            text = ""
        if not bold_text:
            bold_text = ""

        full_text = bold_text + "\n\n" + text + "\n"
        self.buffer.set_text(full_text)
        if text:
            self.clear_tags(full_text)
        start = self.buffer.get_iter_at_offset(0)
        if isinstance(bold_text, str):
            bold_text = unicode(bold_text, "utf-8")
        end = self.buffer.get_iter_at_offset(len(bold_text))
        self.buffer.apply_tag(self.tag_bold, start, end)

    def clear_tags(self, text):
        start_index = 0
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        text_length = len(text)
        while start_index != -1:
            buf_text = self.buffer.get_text(self.buffer.get_iter_at_offset(0),
                                            self.buffer.get_iter_at_offset(text_length),
                                            False)
            start_index = buf_text.find("<")
            if start_index != -1:
                end_index = buf_text.find(">", start_index)
                if end_index != -1:
                    start = self.buffer.get_iter_at_offset(start_index)
                    end = self.buffer.get_iter_at_offset(end_index + 1)
                    self.buffer.delete(start, end)
                else:
                    return


class ScrolledText():
    def __init__(self):
        self.buffer = Gtk.TextBuffer()
        self.text = Gtk.TextView(buffer=self.buffer)
        self.text.set_editable(False)
        self.text.set_cursor_visible(False)
        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll.add(self.text)
