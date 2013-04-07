# -*- coding: utf-8 -*-
'''
Created on Oct 2, 2010

@author: dimitry (zavlab1)
'''

from gi.repository import Gtk
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name
from foobnix.util.const import ICON_FOOBNIX
from foobnix.version import FOOBNIX_VERSION

class AboutWindow(Gtk.AboutDialog):
    def __init__(self):
        Gtk.AboutDialog.__init__(self)
        
        self.set_program_name("Foobnix")
        self.set_version(FOOBNIX_VERSION)
        self.set_copyright("(c) Ivan Ivanenko <ivan.ivanenko@gmail.com>")
        self.set_comments(_("Simple and Powerful player"))
        self.set_website("http://www.foobnix.com")
        self.set_authors(["Dmitry Kozhura (zavlab1) <zavlab1@gmail.com>", "Pietro Campagnano <fain182@gmailcom>", "Viktor Suprun <popsul1993@gmail.com>"])
        
        self.set_translator_credits("""Bernardo Miguel Savone
Sérgio Marques
XsLiDian
KamilSPL
north
Alex Serada
Ivan Ivanenko
Dmitry-Kogura
Fitoschido
zeugma
Schaffino
Oleg «Eleidan» Kulik
Sergey Zigachev
Martino Barbon
Florian Heissenberger
Aldo Mann""")
        
        
        self.set_logo(Gtk.gdk.pixbuf_new_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX))) #@UndefinedVariable
    
    def show(self):
        self.run()
        self.destroy()
