#!/usr/bin/env python

import sys, os, time
import pygtk, gtk, gobject
import pygst
pygst.require("0.10")
import gst

class GTK_Main:
    
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_title("Resolutionchecker")
        window.set_default_size(300, -1)
        window.connect("destroy", gtk.main_quit, "WM destroy")
        vbox = gtk.VBox()
        window.add(vbox)
        self.entry = gtk.Entry()
        vbox.pack_start(self.entry, False, True)
        self.button = gtk.Button("Check")
        self.button.connect("clicked", self.start_stop)
        vbox.add(self.button)
        window.show_all()
        
        self.player = gst.Pipeline("player")
        source = gst.element_factory_make("filesrc", "file-source")
        decoder = gst.element_factory_make("decodebin", "decoder")
        decoder.connect("new-decoded-pad", self.decoder_callback)
        self.fakea = gst.element_factory_make("fakesink", "fakea")
        self.fakev = gst.element_factory_make("fakesink", "fakev")
        
        self.player.add(source, decoder, self.fakea, self.fakev)
        gst.element_link_many(source, decoder)
        
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def start_stop(self, w):
        filepath = self.entry.get_text()
        if os.path.isfile(filepath):
            self.player.set_state(gst.STATE_NULL)
            self.player.get_by_name("file-source").set_property("location", filepath)
            self.player.set_state(gst.STATE_PLAYING)
        else:
            print "FILE not found"
    
    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_STATE_CHANGED:
            if message.parse_state_changed()[1] == gst.STATE_PAUSED:
                for i in self.player.get_by_name("decoder").src_pads():
                    structure_name = i.get_caps()[0].get_name()
                    if structure_name.startswith("video") and len(str(i.get_caps()[0]["width"])) < 6:
                        print "Width:%s, Height:%s" % (i.get_caps()[0]["width"], i.get_caps()[0]["height"])
                        self.player.set_state(gst.STATE_NULL)
                        break
        elif t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.player.set_state(gst.STATE_NULL)

    def decoder_callback(self, decoder, pad, data):
        structure_name = pad.get_caps()[0].get_name()
        if structure_name.startswith("video"):
            fv_pad = self.fakev.get_pad("sink")
            pad.link(fv_pad)
        elif structure_name.startswith("audio"):
            fa_pad = self.fakea.get_pad("sink")
            pad.link(fa_pad)

GTK_Main()
gtk.gdk.threads_init()
gtk.main()
