#-*- coding: utf-8 -*-
'''
Created on Jan 25, 2011

@author: zavlab1
'''

import os
import re
import gtk
import thread
import logging

from subprocess import Popen
from foobnix.util.const import ICON_FOOBNIX
from foobnix.util.audio import get_mutagen_audio
from foobnix.util.localization import foobnix_localization
from foobnix.helpers.textarea import ScrolledText
from foobnix.helpers.window import ChildTopWindow
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name

foobnix_localization()

LOGO = get_foobnix_resourse_path_by_name(ICON_FOOBNIX)

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
        
        f_list = ["  mp3", "  ogg", "  mp2", "  ac3", "  m4a", "  wav"]
        b_list = ["  64 kbps", "  96 kbps", "  128 kbps", "  160 kbps", "  192 kbps", "  224 kbps", "  256 kbps", "  320 kbps", "  448 kbps", "  640 kbps"]
        c_list = ["  1", "  2", "  5"]
        h_list = ["  22050 Hz", "  44100 Hz", "  48000 Hz", "  96000 Hz"]
        
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
        hbox.show_all()
        
        vbox.pack_start(hbox, False)
        
        self.button_box = gtk.HBox(False, 10)
        close_button = gtk.Button(_("Close"))
        close_button.set_size_request(150, 30)
        close_button.connect("clicked", lambda *a: self.hide())
        convert_button = gtk.Button(_("Convert"))
        convert_button.set_size_request(150, 30)
        convert_button.connect("clicked", self.save)
        
        self.progressbar = gtk.ProgressBar()
                
        self.stop_button = gtk.Button(_("Stop"))
        self.stop_button.set_size_request(100, 30)
        self.stop_button.connect("clicked", self.on_stop)
        
        self.progress_box = gtk.HBox()
        self.progress_box.pack_end(self.stop_button, False)
        self.progress_box.pack_end(self.progressbar, True)
                
        vbox.pack_start(self.progress_box, False)
        
        self.button_box.pack_end(convert_button, False)
        self.button_box.pack_end(close_button, False)
        self.button_box.show_all()
        
        vbox.pack_start(self.button_box, False)
        self.add(vbox)
                
    def save(self, *a):
        chooser = gtk.FileChooserDialog(title=_("Choose directory to save converted files"),
                                        action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                        buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        chooser.set_current_folder(os.path.dirname(self.paths[0]))
        chooser.set_icon_from_file(LOGO)
        response = chooser.run()
        
        if response == gtk.RESPONSE_OK:
            format = self.f_combo.get_active_text().strip()
            current_folder = chooser.get_current_folder()
            
            if (os.path.dirname(self.paths[0]) == current_folder and 
            '.'+format == os.path.splitext(self.paths[0])[1]):
                if not self.warning():
                    chooser.destroy()
                    return
            
            self.stop = False
            self.button_box.hide_all()
            self.progressbar.set_fraction(0)
            self.progress_box.show_all()
            
            fraction_length = 1.0 / len(self.paths)
            self.progressbar.set_text("")
            def task():
                for i, path in enumerate(self.paths):
                    self.progressbar.set_text("Convert  %d of %d file(s)"% (i+1, len(self.paths)))
                    self.convert(path, os.path.join(current_folder, os.path.splitext(os.path.basename(path))[0] + "." + format), format)
                    self.progressbar.set_fraction(self.progressbar.get_fraction() + fraction_length)
                    if self.stop:
                        break
                self.progressbar.set_text("Finished (%d of %d)" % (i+1, len(self.paths)))
                self.button_box.show_all()
            thread.start_new_thread(task, ())
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
        elif format == "mp2":
            acodec = "mp2"
        elif format == "ac3":
            acodec = "ac3"
        elif format == "m4a":
            acodec = "libfaac"
        elif format == "wav":
            acodec = "pcm_s16le"
    
        list = ["ffmpeg", "-i", path, "-acodec", acodec, "-ac", channels, "-ab", bitrate, "-ar", samp_rate, '-y', new_path]
        self.ffmpeg = Popen(list, universal_newlines=True)
        self.ffmpeg.wait()
        
    def on_stop(self, *a):
        self.ffmpeg.kill()
        self.stop = True
        
    def fill_form(self, paths):
        self.paths = []
        self.area.buffer.delete(self.area.buffer.get_start_iter(), self.area.buffer.get_end_iter())
        for path in paths:
            if os.path.isfile(path):
                self.paths.append(path)
                self.area.buffer.insert_at_cursor(os.path.basename(path) + "\n")
     
    def warning(self):
        dialog = gtk.Dialog(_("Warning!!!"), buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK, gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        label = gtk.Label(_("Existing files will be overwritten.\nDo you wish to continue?"))
        image = gtk.image_new_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_LARGE_TOOLBAR)
        hbox = gtk.HBox(False, 10)
        hbox.pack_start(image)
        hbox.pack_start(label)
        dialog.vbox.pack_start(hbox)
        dialog.set_icon_from_file(LOGO)
        dialog.set_default_size(210, 100)
        dialog.show_all()
        if dialog.run() == gtk.RESPONSE_OK:
            dialog.destroy()
            return True
        else:
            dialog.destroy()
            return False
        
def combobox_constr(list):
    combobox = gtk.combo_box_new_text()
    for item in list:
        combobox.append_text(item)
    
    return combobox

def convert_files(paths):
    if not globals().has_key("converter"):
        global converter
        converter = Converter()
    converter.show_all()
    converter.progress_box.hide_all()
    converter.fill_form(paths)

class SccrolledText:
    def __init__(self):
        self.buffer = gtk.TextBuffer()
        self.text = gtk.TextView(self.buffer)
        self.text.set_editable(False)
        self.text.set_cursor_visible(False)
        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.scroll.add(self.text)     