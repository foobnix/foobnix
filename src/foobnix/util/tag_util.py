#-*- coding: utf-8 -*-
'''
Created on Jan 25, 2011

@author: zavlab1
'''

import gtk

from foobnix.util.localization import foobnix_localization
from foobnix.util.audio import get_mutagen_audio
from foobnix.helpers.window import ChildTopWindow
import logging


foobnix_localization()

class TagEditor(ChildTopWindow):
    def __init__(self):
        ChildTopWindow.__init__(self, _("Tag Editor"))
        self.set_resizable(True)
        self.set_default_size(400, 150)
        
        artist_label = gtk.Label(_("Artist"))
        title_label = gtk.Label(_("Title"))
        album_label = gtk.Label(_("Album"))
        date_label = gtk.Label(_("Year"))
        tracknumber_label = gtk.Label(_("Track number"))
        genre_label = gtk.Label(_("Genre"))
        author_label = gtk.Label(_("Author text"))
        composer_label = gtk.Label(_("Composer"))

        self.tag_names = ["artist", "title", "album", "date", "tracknumber", "genre", "author", "composer"]

        self.tag_entries = []
        
        self.labels = []

        for tag_name in self.tag_names:
    
            vars()[tag_name + "_entry"] = gtk.Entry()
            self.tag_entries.append(vars()[tag_name + "_entry"])
    
            self.labels.append(vars()[tag_name + "_label"])
    
        lvbox = gtk.VBox(True, 7)
        rvbox = gtk.VBox(True, 7)
        hpan = gtk.HPaned()
        
        for label, tag_entry in zip(self.labels, self.tag_entries):
            lvbox.pack_start(label)
            rvbox.pack_start(tag_entry)
    
        hpan.pack1(lvbox)
        hpan.pack2(rvbox)

        apply_button = gtk.Button(_("Apply"))
        close_button = gtk.Button(_("Close"))

        buttons_hbox = gtk.HBox(True, 10)
        buttons_hbox.pack_start(apply_button)
        buttons_hbox.pack_start(close_button)
        
        vbox = gtk.VBox(False, 15)
        vbox.pack_start(hpan)
        vbox.pack_start(buttons_hbox, True, True, 10)
        
        apply_button.connect("clicked", self.save_audio_tags)
        close_button.connect("clicked", lambda *a: self.hide())
        
        self.add(vbox)
        self.show_all()


    def get_audio_tags(self, path):
        self.audio = get_mutagen_audio(path)
        for tag_name, tag_entry in zip(self.tag_names, self.tag_entries):
            try:
                if self.audio.has_key(tag_name):
                    tag_entry.set_text(self.audio[tag_name][0])
            except AttributeError:
                logging.warn('Can\'t get tags. This is not audio file')
            self.show_all() 
                   
    def save_audio_tags(self, *a):
        for tag_name, tag_entry in zip(self.tag_names, self.tag_entries):
            tag_value = tag_entry.get_text()
            try:
                if self.audio.has_key(tag_name):
                    self.audio[tag_name] = tag_value
                    self.audio.save()
                else:
                    if tag_value:
                        self.audio[tag_name] = [tag_value]
            except AttributeError:
                logging.warn('Can\'t save tags. This is not audio file') 
                
def edit_tags(path=None):
    if not path:
        logging.warn('Can\'t get tags. File not found')
        return
    if not globals().has_key("tag_editor"):
        global tag_editor
        tag_editor = TagEditor()
    tag_editor.get_audio_tags(path)
    