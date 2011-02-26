#-*- coding: utf-8 -*-
'''
Created on Jan 25, 2011

@author: zavlab1
'''
import os
import re
import gtk
import logging

from subprocess import Popen
from foobnix.util.localization import foobnix_localization
from foobnix.util.audio import get_mutagen_audio
#from foobnix.helpers.textarea import ScrolledText
from foobnix.helpers.window import ChildTopWindow

foobnix_localization()

class Converter(ChildTopWindow):
    def __init__(self):
        ChildTopWindow.__init__(self, title="Audio Converter", width=500, height=300)
        self.area = ScrolledText()
        vbox = gtk.VBox(False, 10)
        vbox.pack_start(self.area.scroll)
        vbox.show()
        f_label = gtk.Label(_('Format'))
        b_label = gtk.Label(_('Bitrate'))
        c_label = gtk.Label(_('Channels'))
        h_label = gtk.Label(_('Frequency'))
        
        f_box = gtk.VBox()
        b_box = gtk.VBox()
        c_box = gtk.VBox()
        h_box = gtk.VBox()
        
        f_list = ["  mp3", "  ogg", "  m4a", "  wav"]
        b_list = ["  64 kbps", "  96 kbps", "  128 kbps", "  160 kbps", "  192 kbps", "  224 kbps", "  256 kbps", "  320 kbps"]
        c_list = ["  1", "  2", "  5"]
        h_list = ["  22050 Hz", "  44100 Hz", "  48000 Hz"]
        
        self.f_combo = combobox_constr(f_list)
        self.f_combo.set_active(0)
        self.b_combo = combobox_constr(b_list)
        self.b_combo.set_active(2)
        self.c_combo = combobox_constr(c_list)
        self.c_combo.set_active(1)
        self.h_combo = combobox_constr(h_list)
        self.h_combo.set_active(1)
        
        f_box.pack_start(f_label)
        f_box.pack_start(self.f_combo)
        b_box.pack_start(b_label)
        b_box.pack_start(self.b_combo)
        c_box.pack_start(c_label)
        c_box.pack_start(self.c_combo)
        h_box.pack_start(h_label)
        h_box.pack_start(self.h_combo)
        
        hbox = gtk.HBox(False, 30)
        hbox.pack_start(f_box)
        hbox.pack_start(b_box)
        hbox.pack_start(c_box, False)
        hbox.pack_start(h_box)
        hbox.set_border_width(10)
        
        vbox.pack_start(hbox, False)
        button_box = gtk.HBox(False, 10)
        close_button = gtk.Button(_("Close"))
        close_button.set_size_request(150, 30)
        close_button.connect("clicked", lambda *a: self.hide())
        save_button = gtk.Button(_("Save"))
        save_button.set_size_request(150, 30)
        save_button.connect("clicked", self.on_save)
        
        button_box.pack_end(save_button, False)
        button_box.pack_end(close_button, False)
        vbox.pack_start(button_box, False)
        self.add(vbox)
        self.show_all()
   
    def on_save(self, *a):
        chooser = gtk.FileChooserDialog(title=_("Choose directory to save converted files"),
                                        action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        chooser.set_current_folder(os.path.dirname(self.paths[0]))
        response = chooser.run()
        format = self.f_combo.get_active_text().strip()
        if response == gtk.RESPONSE_OK:
            current_folder = chooser.get_current_folder()
            for path in self.paths:
                self.convert(path, os.path.join(current_folder, os.path.splitext(os.path.basename(path))[0] + "." + format), format)
        chooser.destroy()   
    
    def convert(self, path, new_path, format):
        b_text = self.b_combo.get_active_text()
        bitrate = re.search('^([0-9]{1,5})', b_text.strip()).group() + 'k'
        c_text = self.c_combo.get_active_text()
        channels = re.search('^([0-9]{1,5})', c_text.strip()).group()                 
        h_text = self.h_combo.get_active_text()
        samp_rate = re.search('^([0-9]{1,5})', h_text.strip()).group()
        
        if format == "mp3":
            acodec = "libmp3lame"
        elif format == "ogg":
            acodec = "libvorbis"
        elif format == "m4a":
            acodec = "libfaac"
        elif format == "wav":
            acodec = "pcm_s16le"
    
        list = ["ffmpeg", "-i", path, "-acodec", acodec, "-ac", channels, "-ab", bitrate, "-ar", samp_rate, new_path]
        ffmpeg = Popen(list, universal_newlines=True)
        
    def fill_form(self, paths):
        self.paths = []
        self.area.buffer.delete(self.area.buffer.get_start_iter(), self.area.buffer.get_end_iter())
        for path in paths:
            if os.path.isfile(path):
                self.paths.append(path)
                self.area.buffer.insert_at_cursor(os.path.basename(path) + "\n")
                    
def combobox_constr(list):
    combobox = gtk.combo_box_new_text()
    for item in list:
        combobox.append_text(item)
    
    return combobox

def convert_files(paths):
    if not globals().has_key("converter"):
        global converter
        converter = Converter()
    else:
        converter.show_all()
    converter.fill_form(paths)

class ScrolledText:
    def __init__(self):
        self.buffer = gtk.TextBuffer()
        self.text = gtk.TextView(self.buffer)
        self.text.set_editable(False)
        self.text.set_cursor_visible(False)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self.text)     