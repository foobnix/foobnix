#-*- coding: utf-8 -*-
'''
Created on Jan 25, 2011

@author: zavlab1
'''

from __future__ import with_statement

import os
import re
import thread
import logging

from gi.repository import Gtk
from gi.repository import GLib
from subprocess import Popen, PIPE

from foobnix.fc.fc_helper import CONFIG_DIR
from foobnix.util.const import ICON_FOOBNIX
from foobnix.util.file_utils import open_in_filemanager
from foobnix.util.localization import foobnix_localization
from foobnix.helpers.textarea import ScrolledText
from foobnix.helpers.window import ChildTopWindow
from foobnix.gui.service.path_service import get_foobnix_resourse_path_by_name

foobnix_localization()

LOGO = get_foobnix_resourse_path_by_name(ICON_FOOBNIX)
FFMPEG_NAME = "ffmpeg_foobnix"
#fix win
if os.name == 'posix':
    if os.uname()[4] == 'x86_64':
        FFMPEG_NAME += "_x64"

class Converter(ChildTopWindow):
    def __init__(self):
        ChildTopWindow.__init__(self, title="Audio Converter", width=500, height=400)

        self.area = ScrolledText()
        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 10)
        vbox.pack_start(self.area.scroll)
        vbox.show()
        format_label = Gtk.Label.new(_('Format'))
        bitrate_label = Gtk.Label.new(_('Bitrate'))
        channels_label = Gtk.Label.new(_('Channels'))
        hertz_label = Gtk.Label.new(_('Frequency'))

        format_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        bitrate_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        channels_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        hertz_box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.format_list = ["Choose", "  mp3", "  ogg", "  mp2", "  ac3", "  m4a", "  wav"]
        self.bitrate_list = ["  64 kbps", "  96 kbps", "  128 kbps", "  160 kbps", "  192 kbps", "  224 kbps", "  256 kbps", "  320 kbps", "  384 kbps", "  448 kbps", "  640 kbps"]
        self.channels_list = ["  1", "  2", "  6"]
        self.hertz_list = ["  22050 Hz", "  44100 Hz", "  48000 Hz", "  96000 Hz"]

        self.format_combo = combobox_constr(self.format_list)
        self.format_combo.connect("changed", self.on_change_format)

        self.bitrate_combo = combobox_constr()
        self.channels_combo = combobox_constr()
        self.hertz_combo = combobox_constr()

        format_box.pack_start(format_label, False, False, 0)
        format_box.pack_start(self.format_combo, False, False, 0)
        bitrate_box.pack_start(bitrate_label, False, False, 0)
        bitrate_box.pack_start(self.bitrate_combo, False, False, 0)
        channels_box.pack_start(channels_label, False, False, 0)
        channels_box.pack_start(self.channels_combo, False, False, 0)
        hertz_box.pack_start(hertz_label, False, False, 0)
        hertz_box.pack_start(self.hertz_combo, False, False, 0)

        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 30)
        hbox.pack_start(format_box, False, False, 0)
        hbox.pack_start(bitrate_box, False, False, 0)
        hbox.pack_start(channels_box, False, False, 0)
        hbox.pack_start(hertz_box, False, False, 0)
        hbox.set_border_width(10)
        hbox.show_all()

        vbox.pack_start(hbox, False)

        self.button_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        close_button = Gtk.Button.new_with_label(_("Close"))
        close_button.set_size_request(150, 30)
        close_button.connect("clicked", lambda *a: self.hide())
        self.convert_button = Gtk.Button.new_with_label(_("Convert"))
        self.convert_button.set_size_request(150, 30)
        self.convert_button.connect("clicked", self.save)

        self.progressbar = Gtk.ProgressBar()

        self.stop_button = Gtk.Button.new_with_label(_("Stop"))
        self.stop_button.set_size_request(100, 30)
        self.stop_button.connect("clicked", self.on_stop)

        self.open_folder_button = Gtk.Button.new_with_label(_("Show files"))
        self.open_folder_button.connect('released', self.open_in_fm)

        self.progress_box = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.progress_box.pack_end(self.open_folder_button, False)
        self.progress_box.pack_end(self.stop_button, False)
        self.progress_box.pack_end(self.progressbar, True)

        self.output = ScrolledText()
        self.output.text.set_size_request(-1, 50)
        self.output.scroll.set_size_request(-1, 50)
        self.output.scroll.set_placement(Gtk.CornerType.BOTTOM_LEFT)
        vbox.pack_start(self.progress_box, False)

        self.button_box.pack_end(self.convert_button, False)
        self.button_box.pack_end(close_button, False)

        self.button_box.show_all()

        vbox.pack_start(self.button_box, False)
        vbox.pack_start(self.output.scroll, False)
        self.add(vbox)

    def save(self, *a):
        chooser = Gtk.FileChooserDialog(title=_("Choose directory to save converted files"),
                                        action=Gtk.FileChooserAction.SELECT_FOLDER,
                                        buttons=("document-save", Gtk.ResponseType.OK))
        chooser.set_current_folder(os.path.dirname(self.paths[0]))
        chooser.set_icon_from_file(LOGO)
        response = chooser.run()

        if response == Gtk.ResponseType.OK:
            format = self.format_combo.get_active_text().strip()
            self.current_folder = chooser.get_current_folder()

            for path in self.paths:
                if (os.path.splitext(os.path.basename(path))[0] + '.' + format) in os.listdir(self.current_folder):
                    if not self.warning():
                        chooser.destroy()
                        return
                    else:
                        break
            self.stop = False
            self.button_box.hide_all()
            self.progressbar.set_fraction(0)
            self.progress_box.show_all()
            self.output.scroll.show()

            fraction_length = 1.0 / len(self.paths)
            self.progressbar.set_text("")
            self.output.buffer.delete(self.output.buffer.get_start_iter(), self.output.buffer.get_end_iter())
            def task():
                self.stop_button.show()
                self.open_folder_button.hide()
                for i, path in enumerate(self.paths):
                    self.progressbar.set_text("Convert  %d of %d file(s)" % (i+1, len(self.paths)))
                    self.convert(path, os.path.join(self.current_folder, os.path.splitext(os.path.basename(path))[0] + "." + format), format)
                    self.progressbar.set_fraction(self.progressbar.get_fraction() + fraction_length)
                    if self.stop:
                        self.open_folder_button.show()
                        self.progressbar.set_text("Stopped . Converted %d of %d file(s)" % (i, len(self.paths)))
                        break
                    else:
                        self.progressbar.set_text("Finished (%d of %d)" % (i+1, len(self.paths)))
                self.stop_button.hide()
                self.open_folder_button.show()
                self.button_box.show_all()
            thread.start_new_thread(task, ())
        chooser.destroy()

    def convert(self, path, new_path, format):
        bitrate_text = self.bitrate_combo.get_active_text()
        if bitrate_text:
            bitrate = re.search('^([0-9]{1,5})', bitrate_text.strip()).group() + 'k'
        else:
            bitrate = ""
        channels_text = self.channels_combo.get_active_text()
        channels = re.search('^([0-9]{1,5})', channels_text.strip()).group()
        hertz_text = self.hertz_combo.get_active_text()
        samp_rate = re.search('^([0-9]{1,5})', hertz_text.strip()).group()

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
        else:
            logging.error('Unsupported format')
            return

        list = [os.path.join(CONFIG_DIR, FFMPEG_NAME), "-i", path, "-acodec", acodec, "-ac", channels, "-ab", bitrate, "-ar", samp_rate, '-y', new_path]

        if format == "wav":
            list.remove("-ab")
            list.remove(bitrate)

        logging.debug(" ".join(list))

        self.ffmpeg = Popen(list, universal_newlines=True, stderr=PIPE)

        for line in iter(self.ffmpeg.stderr.readline, ""):
            GLib.idle_add(self.output.buffer.insert_at_cursor, line)
            logging.debug(line)
            adj = self.output.scroll.get_vadjustment()
            GLib.idle_add(adj.set_value, adj.get_upper() - adj.get_page_size() + 1)

        self.ffmpeg.wait()

    def on_stop(self, *a):
        self.ffmpeg.terminate()
        self.stop = True
        #self.open_folder_button.show()

    def fill_form(self, paths):
        self.paths = []
        self.area.buffer.delete(self.area.buffer.get_start_iter(), self.area.buffer.get_end_iter())
        for path in paths:
            if os.path.isfile(path):
                self.paths.append(path)
                self.area.buffer.insert_at_cursor(os.path.basename(path) + "\n")

    def warning(self):
        dialog = Gtk.Dialog(_("Warning!!!"))
        ok_button = dialog.add_button("dialog-ok", Gtk.ResponseType.OK) #@UnusedVariable
        cancel_button = dialog.add_button("dialog-cancel", Gtk.ResponseType.CANCEL)
        cancel_button.grab_default()
        label = Gtk.Label.new(_("So file(s)  already exist(s) and will be overwritten.\nDo you wish to continue?"))
        image = Gtk.Image.new_from_icon_name("dialog-warning", Gtk.IconSize.LARGE_TOOLBAR)
        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        hbox.pack_start(image)
        hbox.pack_start(label)
        dialog.vbox.pack_start(hbox)
        dialog.set_icon_from_file(LOGO)
        dialog.set_default_size(210, 100)
        dialog.show_all()
        if dialog.run() == Gtk.ResponseType.OK:
            dialog.destroy()
            return True
        else:
            dialog.destroy()
            return False

    def remake_combos(self, bitrate_list, channels_list, hertz_list):
        self.clear_combos(self.bitrate_combo, self.channels_combo, self.hertz_combo)
        for b in bitrate_list:
            self.bitrate_combo.append_text(b)
        for c in channels_list:
            self.channels_combo.append_text(c)
        for h in hertz_list:
            self.hertz_combo.append_text(h)

    def clear_combos(self, *combo_list):
        if not combo_list:
            return
        for combo in combo_list:
            combo.remove_all()
            #for i in self.bitrate_list: #the longest list
            #    combo.remove()

    def on_change_format(self, a):
        bitrate_list = self.bitrate_list[:]
        channels_list = self.channels_list[:]
        hertz_list = self.hertz_list[:]

        bitrate_index = 6
        channels_index = 1
        hertz_index = 2

        if self.format_combo.get_active_text() == "  mp3":
            bitrate_list.remove("  640 kbps")
            bitrate_list.remove("  448 kbps")
            bitrate_list.remove("  384 kbps")
            channels_list.remove("  6")
            hertz_list.remove("  96000 Hz")
            hertz_index = 1
        elif self.format_combo.get_active_text() == "  mp2":
            bitrate_list.remove("  640 kbps")
            bitrate_list.remove("  448 kbps")
            hertz_list.remove("  96000 Hz")
            hertz_list.remove("  44100 Hz")
            hertz_list.remove("  22050 Hz")
            hertz_index = 0
        elif self.format_combo.get_active_text() == "  ac3":
            hertz_list.remove("  96000 Hz")
        elif self.format_combo.get_active_text() == "  m4a":
            bitrate_list.remove("  640 kbps")

        self.remake_combos(bitrate_list, channels_list, hertz_list)

        self.bitrate_combo.set_active(bitrate_index)
        self.channels_combo.set_active(channels_index)
        self.hertz_combo.set_active(hertz_index)

        if self.format_combo.get_active() == 0:
            self.clear_combos(self.bitrate_combo, self.channels_combo, self.hertz_combo)
            self.convert_button.set_sensitive(False)
            self.bitrate_combo.set_sensitive(False)
            self.channels_combo.set_sensitive(False)
            self.hertz_combo.set_sensitive(False)
        else:
            self.convert_button.set_sensitive(True)

        if self.format_combo.get_active_text() == "  wav":
            self.clear_combos(self.bitrate_combo)
            self.bitrate_combo.set_sensitive(False)
        else:
            self.bitrate_combo.set_sensitive(True)
            self.channels_combo.set_sensitive(True)
            self.hertz_combo.set_sensitive(True)

    def open_in_fm(self, *a):
        open_in_filemanager(self.current_folder)

def combobox_constr(list=None):
    combobox = Gtk.ComboBoxText()
    if not list:
        return combobox

    for item in list:
        combobox.append_text(item)

    return combobox

def convert_files(paths):
    if FFMPEG_NAME in os.listdir(CONFIG_DIR):
        if not globals().has_key("converter"):
            global converter
            converter = Converter()
        converter.show_all()
        converter.progress_box.hide_all()
        converter.output.scroll.hide()
        converter.fill_form(paths)
        converter.format_combo.set_active(0)
    else:
        url = "http://foobnix.com/assets/downloads/" + FFMPEG_NAME
        dialog = Gtk.Dialog(_("Attention"))
        area = ScrolledText()
        area.buffer.set_text(_("Converter require specially compiled ffmpeg module for work.\n" +
                               "You should download it automatically (click Download)\n"+
                               "Also check if you have packages libmp3lame0 and libfaac0"))
        ok_button = dialog.add_button(_("Download"), Gtk.ResponseType.OK)

        cancel_button = dialog.add_button("dialog-cancel", Gtk.ResponseType.CANCEL)
        ok_button.grab_default()
        prog_bar = Gtk.ProgressBar()
        dialog.vbox.pack_start(area.scroll)
        dialog.vbox.pack_start(prog_bar, False)
        dialog.set_icon_from_file(LOGO)
        dialog.set_default_size(400, 150)
        dialog.show_all()
        prog_bar.hide()
        canceled = False
        if dialog.run() == Gtk.ResponseType.OK:
            prog_bar.show()
            import urllib2
            remote_file = urllib2.urlopen(url)
            size = float(remote_file.info()['Content-Length'])
            ffmpeg_path = os.path.join(CONFIG_DIR, FFMPEG_NAME)

            def on_close(*a):
                if os.path.isfile(ffmpeg_path) and os.path.getsize(ffmpeg_path) < size:
                    os.remove(ffmpeg_path)
                dialog.destroy()
                return
            cancel_button.connect("released", on_close)

            def task():
                with open(ffmpeg_path, 'wb') as local_file:
                    got = 0
                    cycle = True
                    while cycle and not canceled:
                        try:
                            local_file.write(remote_file.read(20000))
                            if got + 20000 >= size:
                                cycle = False
                            got = os.path.getsize(ffmpeg_path)

                            def subtask():
                                prog_bar.set_fraction(got/size)
                                prog_bar.set_text("Downloaded  %.2f of %.2fMb" % (float(got)/1024/1024, size/1024/1024))

                            GLib.idle_add(subtask)
                        except OSError as e:
                            if os.path.isfile(ffmpeg_path) and os.path.getsize(ffmpeg_path) < size:
                                os.remove(ffmpeg_path)

                os.chmod(ffmpeg_path, 0777)
                GLib.idle_add(convert_files, paths)
                dialog.destroy()

            thread.start_new_thread(task, ())
        else:
            dialog.destroy()
