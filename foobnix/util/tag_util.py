#-*- coding: utf-8 -*-
'''
Created on Jan 25, 2011

@author: zavlab1
'''

from gi.repository import Gtk
import logging
import os.path
import thread

from foobnix.util.id3_util import correct_encoding
from foobnix.util.audio import get_mutagen_audio
from foobnix.helpers.window import ChildTopWindow
from mutagen.easyid3 import EasyID3
from foobnix.util.localization import foobnix_localization
from mutagen.mp4 import MP4, MP4MetadataValueError

foobnix_localization()

class TagEditor(ChildTopWindow):
    def __init__(self, controls):
        ChildTopWindow.__init__(self, _("Tag Editor"))
        self.controls = controls

        self.store = {}

        self.set_resizable(True)
        self.set_default_size(430, 150)

        """make tooltip more quick (useful for checkbuttons)"""
        Gtk.Settings().set_property('gtk-tooltip-timeout', 0)


        artist_label = Gtk.Label.new(_("Artist")) #@UnusedVariable
        title_label = Gtk.Label.new(_("Title")) #@UnusedVariable
        album_label = Gtk.Label.new(_("Album")) #@UnusedVariable
        date_label = Gtk.Label.new(_("Year")) #@UnusedVariable
        tracknumber_label = Gtk.Label.new(_("Track number")) #@UnusedVariable
        genre_label = Gtk.Label.new(_("Genre")) #@UnusedVariable
        author_label = Gtk.Label.new(_("Author text")) #@UnusedVariable
        composer_label = Gtk.Label.new(_("Composer")) #@UnusedVariable

        self.paths = []
        self.tag_names = ["artist", "title", "album", "date", "tracknumber", "genre", "author", "composer"]
        self.tag_mp4_names = ['\xa9ART', '\xa9nam', '\xa9alb', '\xa9day', 'trkn', '\xa9gen', '', '\xa9wrt']
        self.tag_entries = []
        self.labels = []
        self.check_buttons = []
        self.hboxes = []

        for tag_name in self.tag_names:

            vars()[tag_name + "_entry"] = Gtk.Entry()
            self.tag_entries.append(vars()[tag_name + "_entry"])

            self.labels.append(vars()[tag_name + "_label"])

            vars()[tag_name + "_chbutton"] = Gtk.CheckButton.new()
            self.check_buttons.append(vars()[tag_name + "_chbutton"])
#
            check_button = self.check_buttons[-1]

            check_button.set_focus_on_click(False)
            check_button.set_tooltip_text(_("Apply for all selected tracks\n(active on multi selection)"))

            vars()[tag_name + "_hbox"] = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 5)
            self.hboxes.append(vars()[tag_name + "_hbox"])

            self.hboxes[-1].pack_end(check_button, False, False)
            self.hboxes[-1].pack_end(self.tag_entries[-1], True, True)


        lvbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 7)
        lvbox.set_homogeneous(True)
        rvbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 7)
        rvbox.set_homogeneous(True)

        hpan = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)

        for label, hbox in zip(self.labels, self.hboxes):
            lvbox.pack_start(label)
            rvbox.pack_start(hbox)

        hpan.pack1(lvbox)
        hpan.pack2(rvbox)

        apply_button = Gtk.Button.new_with_label(_("Apply"))
        close_button = Gtk.Button.new_with_label(_("Close"))

        buttons_hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 10)
        buttons_hbox.set_homogeneous(True)
        buttons_hbox.pack_start(apply_button)
        buttons_hbox.pack_start(close_button)

        vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 15)
        vbox.pack_start(hpan)
        vbox.pack_start(buttons_hbox, True, True, 10)

        apply_button.connect("clicked", self.save_audio_tags, self.paths)
        close_button.connect("clicked", lambda * a: self.hide())

        self.add(vbox)
        self.show_all()
    """
    def apply_changes_for_rows_in_tree(self):
        ''' apply stored changes for rows in playlist_tree '''
        texts = {}
        artists = {}
        titles = {}
        composers = {}
        albums = {}

        playlist_tree = self.controls.notetabs.get_current_tree()

        for path in self.store.keys():
            if self.store[path][0] and self.store[path][1]:
                artists[path] = self.store[path][0]
                titles[path] = self.store[path][1]
            elif self.store[path][0] and not self.store[path][1]:
                artists[path] = self.store[path][0]
                titles[path] = _('Unknown title')
            elif self.store[path][1] and not self.store[path][0]:
                artists[path] = _('Unknown artist')
                titles[path] = self.store[path][1]

            if artists.has_key(path):
                texts[path] = artists[path] + ' - ' + titles[path]
            else:
                texts[path] = os.path.basename(path)
                artists[path] = ""
                titles[path] = ""

            if artists[path] == _('Unknown artist'):
                artists[path] = ""
            if titles[path] == _('Unknown title'):
                titles[path] == ""

            if self.store[path][2]:
                composers[path] = self.store[path][2]
            if self.store[path][3]:
                albums[path] = self.store[path][3]

        for path in self.store.keys():
            for row in playlist_tree.model:
                if row[playlist_tree.path[0]] == path:
                    if path in texts:
                        row[playlist_tree.text[0]] = texts[path]
                        row[playlist_tree.artist[0]] = artists[path]
                        row[playlist_tree.title[0]] = titles[path]
                    if path in composers:
                        row[playlist_tree.composer[0]] = composers[path]
                    if path in albums:
                        row[playlist_tree.album[0]] = albums[path]
        self.store = {}
    """

    def get_audio_tags(self, paths):
        self.paths = paths
        if len(paths) == 1:
            for chbutton in self.check_buttons:
                chbutton.set_sensitive(False)
        else:
            for chbutton in self.check_buttons:
                chbutton.set_sensitive(True)

        self.audious = []
        for path in paths[:]:
            if not path or os.path.isdir(path):
                self.paths.remove(path)
                continue
            audio = get_mutagen_audio(path)

            if not audio:
                try:
                    audio.add_tags(ID3=EasyID3)
                except Exception, e:
                    logging.error(e)

            self.decoding_cp866(audio)
            self.audious.append(audio)


        if isinstance(self.audious[0], MP4):
            tag_names = self.tag_mp4_names
            '''make author entry not sensitive because mp4 hasn't so tag'''
            self.tag_entries[-2].set_sensitive(False)
            self.check_buttons[-2].set_sensitive(False)
            self.labels[-2].set_sensitive(False)
        else:
            tag_names = self.tag_names
        for tag_name, tag_entry in zip(tag_names, self.tag_entries):
            tag_entry.delete_text(0, -1)
            try:
                if self.audious[0].has_key(tag_name):
                    tag_entry.set_text(self.audious[0][tag_name][0])
                else:
                    tag_entry.set_text('')
            except AttributeError:
                logging.warn('Can\'t get tags. This is not audio file')
            except TypeError, e:
                if isinstance(self.audious[0][tag_name][0], tuple):
                    tag_entry.set_text(str(self.audious[0][tag_name][0]).strip('()'))
                else:
                    logging.error(e)
        self.show_all()

    def save_audio_tags(self, button, paths):

        def set_tags(audio, path, tag_name):
            if not self.store.has_key(path):
                self.store[path] = ["", "", "", ""]
            if isinstance(audio, MP4):
                tag_name = tag_mp4_name
            try:
                if audio.has_key(tag_name):
                    if not tag_value:
                        del audio[tag_name]
                        audio.save()
                        return
                    audio[tag_name] = tag_value
                else:
                    if tag_value:
                        audio[tag_name] = [tag_value]
                audio.save()

            except AttributeError:
                logging.warn('Can\'t save tags. Perhaps' + os.path.split(path)[1] + ' is not audio file')
            except MP4MetadataValueError:
                '''for mp4 trkn is tuple'''
                new_tag_value = [tuple(map(int, tag_value.split(', ')))]
                audio[tag_name] = new_tag_value
                audio.save()

            """
            ''' store changes '''
            if (tag_name == "artist" or tag_name == '\xa9ART') and tag_value:
                self.store[path][0] = tag_value
                try:
                    if audio.has_key("title"):
                        self.store[path][1] = audio["title"][0]
                    elif audio.has_key('\xa9nam'):
                        self.store[path][1] = audio['\xa9nam'][0]
                except UnicodeDecodeError:
                    pass
            elif (tag_name == "title" or tag_name == '\xa9nam') and tag_value:
                self.store[path][1] = tag_value
                try:
                    if audio.has_key("artist"):
                        self.store[path][0] = audio["artist"][0]
                    elif audio.has_key('\xa9ART'):
                        self.store[path][0] = audio['\xa9ART']
                except UnicodeDecodeError:
                    pass
            if (tag_name == "composer" or tag_name == '\xa9wrt') and tag_value:
                self.store[path][2] = tag_value
            if (tag_name == "album" or tag_name == '\xa9alb') and tag_value:
                self.store[path][3] = tag_value
            """


        for tag_name, tag_mp4_name, tag_entry, check_button in zip(self.tag_names, self.tag_mp4_names, self.tag_entries, self.check_buttons):
            tag_value = tag_entry.get_text()
            if check_button.get_active():
                for audio, path in zip(self.audious, self.paths):
                    set_tags(audio, path, tag_name)
            else:
                set_tags(self.audious[0], self.paths[0], tag_name)

            check_button.set_active(False)

        #self.apply_changes_for_rows_in_tree()

        self.hide()

        self.controls.notetabs.get_current_tree().change_rows_by_path(self.paths)


    def decoding_cp866(self, audio):
        if not audio:
            return
        if not isinstance(audio, MP4):
            for value, key in zip(audio.values(), audio.keys()):
                audio[key] = correct_encoding(value[0])

def edit_tags(a):
    controls, paths = a
    if not globals().has_key("tag_editor"):
        global tag_editor
        tag_editor = TagEditor(controls)
    tag_editor.get_audio_tags(paths)


