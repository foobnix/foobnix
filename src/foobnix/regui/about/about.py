# -*- coding: utf-8 -*-
'''
Created on Oct 2, 2010

@author: dimitry (zavlab1)
'''

import gtk
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name
from foobnix.util.const import ICON_FOOBNIX
from foobnix.version import FOOBNIX_VERSION

class AboutWindow(gtk.AboutDialog):
    def __init__(self):
        gtk.AboutDialog.__init__(self)
        
        self.set_program_name("Foobnix")
        self.set_version(FOOBNIX_VERSION)
        self.set_copyright("(c) Ivan Ivanenko <ivan.ivanenko@gmail.com>")
        self.set_comments(_("Simple and Powerful player"))
        self.set_website("http://www.foobnix.com")
    
        self.set_authors(["Dmitry Kozhura (zavlab1) <zavlab1@gmail.com>", "Pietro Campagnano <fain182@gmailcom>"])
        self.set_logo(gtk.gdk.pixbuf_new_from_file(get_foobnix_resourse_path_by_name(ICON_FOOBNIX)))
    
    def show(self):
        self.run()
        self.destroy()
