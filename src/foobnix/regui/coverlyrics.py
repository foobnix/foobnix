'''
Created on Apr 17, 2011

@author: zavlab1
'''

import gtk
from foobnix.fc.fc import FC

from foobnix.helpers.image import ImageBase
from foobnix.helpers.textarea import TextArea
from foobnix.util.const import ICON_BLANK_DISK


class CoverLyricsPanel(gtk.Frame):
    def __init__(self, controls):
        gtk.Frame.__init__(self)
        vbox = gtk.VBox(False, 5)
        self.controls = controls
        
        self.album_title = gtk.Label(_("Album title"))
        image_size = FC().main_window_size[2] - (FC().hpaned_right + 16)
        self.image = ImageBase(ICON_BLANK_DISK, size=image_size)
        image_frame = gtk.Frame()
        image_frame.add(self.image)
        image_frame.set_label_widget(gtk.Label(_("Cover:")))
        vbox.pack_start(image_frame, False)
        
        self.lyrics = TextArea()
        lyrics_frame = gtk.Frame()
        lyrics_frame.add(self.lyrics)
        lyrics_frame.set_label_widget(gtk.Label(_("Lyric:")))
        vbox.pack_start(lyrics_frame, True)
        
        self.add(vbox)
        self.set_label_widget(self.album_title) 
        self.show_all()
        
    def get_pixbuf(self):
        return self.controls.info_panel.image.pixbuf
        
    def set_cover(self):
        pixbuf = self.get_pixbuf()
        self.image.set_from_pixbuf(pixbuf)
       