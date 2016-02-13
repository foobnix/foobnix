#-*- coding: utf-8 -*-
'''
Created on 24 авг. 2010

@author: ivan
'''
from gi.repository import Gtk
from foobnix.preferences.config_plugin import ConfigPlugin
class CategoryInfoConfig(ConfigPlugin):
    name = _("Category Info")
    def __init__(self):
        box = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        box.hide()

        similar_arists = Gtk.CheckButton.new_with_label(_"Show Similar Artists")
        similar_arists.show()

        similar_song = Gtk.CheckButton.new_with_label(_"Show Similar Songs")
        similar_song.show()

        similar_tags = Gtk.CheckButton.new_with_label(_"Show Similar Tags")
        similar_tags.show()

        box.pack_start(similar_arists, False, True, 0)
        box.pack_start(similar_song, False, True, 0)
        box.pack_start(similar_tags, False, True, 0)

        self.widget = box
