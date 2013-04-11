'''
Created on Apr 17, 2011

@author: zavlab1
'''

from gi.repository import Gtk

from foobnix.fc.fc import FC
from foobnix.helpers.image import ImageBase
from foobnix.helpers.textarea import TextArea
from foobnix.util.const import ICON_BLANK_DISK


class CoverLyricsPanel(Gtk.Frame):
    def __init__(self, controls):
        Gtk.Frame.__init__(self)
        vbox = Gtk.VBox(False, 5)
        self.controls = controls
        self.set_size_request(100, 200)
        self.album_title = Gtk.Label(_("Album title"))
        image_size = FC().main_window_size[2] - (FC().hpaned_right + 16)
        self.image = ImageBase(ICON_BLANK_DISK, size=image_size)
        image_frame = Gtk.Frame()
        image_frame.add(self.image)
        image_frame.set_label_widget(Gtk.Label(_("Cover:")))
        vbox.pack_start(image_frame, False, False, 0)
        
        self.lyrics = TextArea()
        lyrics_frame = Gtk.Frame()
        lyrics_frame.add(self.lyrics)
        lyrics_frame.set_label_widget(Gtk.Label(_("Lyric:")))
        vbox.pack_start(lyrics_frame, True, False, 0)
        
        self.add(vbox)
        self.set_label_widget(self.album_title) 
        self.show_all()
                
    def get_pixbuf(self):
        return self.controls.info_panel.image.pixbuf
        
    def set_cover(self):
        pixbuf = self.get_pixbuf()
        self.image.set_from_pixbuf(pixbuf)
        
    def adapt_image(self):
        if self.lyrics.get_property("visible"):
            self.image.size = self.lyrics.get_allocation().width
            self.image.set_from_pixbuf(self.controls.coverlyrics.get_pixbuf())
        