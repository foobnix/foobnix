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
import os.path
from mutagen.mp4 import MP4, MP4MetadataValueError


foobnix_localization()

class TagEditor(ChildTopWindow):
    def __init__(self):
        ChildTopWindow.__init__(self, _("Tag Editor"))
        self.set_resizable(True)
        self.set_default_size(430, 150)
        
        """make tooltip more quick (useful for checkbuttons)"""
        gtk.Settings().set_property('gtk-tooltip-timeout', 0)
        
        artist_label = gtk.Label(_("Artist"))
        title_label = gtk.Label(_("Title"))
        album_label = gtk.Label(_("Album"))
        date_label = gtk.Label(_("Year"))
        tracknumber_label = gtk.Label(_("Track number"))
        genre_label = gtk.Label(_("Genre"))
        author_label = gtk.Label(_("Author text"))
        composer_label = gtk.Label(_("Composer"))
        
        self.paths = []
        self.tag_names = ["artist", "title", "album", "date", "tracknumber", "genre", "author", "composer"]
        self.tag_mp4_names = ['\xa9ART', '\xa9nam', '\xa9alb', '\xa9day', 'trkn', '\xa9gen', '', '\xa9wrt']
        self.tag_entries = []
        self.labels = []
        self.check_buttons = []
        self.hboxes = []
           
        for tag_name in self.tag_names:
    
            vars()[tag_name + "_entry"] = gtk.Entry()
            self.tag_entries.append(vars()[tag_name + "_entry"])
    
            self.labels.append(vars()[tag_name + "_label"])
            
            vars()[tag_name + "_chbutton"] = gtk.CheckButton()
            self.check_buttons.append(vars()[tag_name + "_chbutton"])
#           chbutton_image = gtk.image_new_from_stock(gtk.STOCK_COPY, gtk.ICON_SIZE_SMALL_TOOLBAR)
            
            check_button = self.check_buttons[-1]
            #check_button.add(chbutton_image)
            
            check_button.set_focus_on_click(False) 
            check_button.set_tooltip_text(_("Apply for all selected tracks\n(active on multi selection)"))
            
            vars()[tag_name + "_hbox"] = gtk.HBox(False, 5)
            self.hboxes.append(vars()[tag_name + "_hbox"])
            
            self.hboxes[-1].pack_end(check_button, False, False)
            self.hboxes[-1].pack_end(self.tag_entries[-1], True, True)
            
    
        lvbox = gtk.VBox(True, 7)
        rvbox = gtk.VBox(True, 7)
        hpan = gtk.HPaned()
        
        for label, hbox in zip(self.labels, self.hboxes):
            lvbox.pack_start(label)
            rvbox.pack_start(hbox)
    
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
        
        apply_button.connect("clicked", self.save_audio_tags, self.paths)
        close_button.connect("clicked", lambda * a: self.hide())
        
        self.add(vbox)
        self.show_all()

    
    def get_audio_tags(self, paths):
        self.paths = paths
        if len(paths) == 1:
            for chbutton in self.check_buttons:
                chbutton.set_sensitive(False)
                #chbutton.set_relief(gtk.RELIEF_NONE)
        else: 
            for chbutton in self.check_buttons:
                chbutton.set_sensitive(True)
                #chbutton.set_relief(gtk.RELIEF_NORMAL)           
        
        self.audious = []
        for path in paths:
            self.audious.append(get_mutagen_audio(path))
        
        if isinstance(self.audious[0], MP4):
            tag_names = self.tag_mp4_names
            #make author entry not sensitive because mp4 hasn't so tag
            self.tag_entries[-2].set_sensitive(False)
            self.check_buttons[-2].set_sensitive(False)
            self.labels[-2].set_sensitive(False)
        else:
            tag_names = self.tag_names
        for tag_name, tag_entry in zip(tag_names, self.tag_entries):
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
            if isinstance(audio, MP4):
                tag_name = tag_mp4_name
            try:
                if audio.has_key(tag_name):
                    audio[tag_name] = tag_value
                else:
                    if tag_value:
                        audio[tag_name] = [tag_value]
                audio.save()
            except AttributeError:
                logging.warn('Can\'t save tags. ' + os.path.split(path)[1] + ' is not audio file') 
            except MP4MetadataValueError:
                #for mp4 trkn is tuple
                new_tag_value = [tuple(map(int, tag_value.split(', ')))]
                audio[tag_name] = new_tag_value
                audio.save()
                          
        for tag_name, tag_mp4_name, tag_entry, check_button in zip(self.tag_names, self.tag_mp4_names, self.tag_entries, self.check_buttons):
            tag_value = tag_entry.get_text()
            if check_button.get_active():
                for audio, path in zip(self.audious, self.paths):
                    set_tags(audio, path, tag_name)
            else:
                set_tags(self.audious[0], self.paths[0], tag_name)
            check_button.set_active(False)
            
            
                
def edit_tags(paths=None):
    if not paths:
        logging.warn('Can\'t get tags. Files not found')
        return
    if not globals().has_key("tag_editor"):
        global tag_editor
        tag_editor = TagEditor()
    tag_editor.get_audio_tags(paths)
    
    
