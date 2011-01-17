# -*- coding: utf-8 -*-
'''
Created on Oct 2, 2010

@author: dimitry (zavlab1)
'''

import gtk
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name
from foobnix.helpers.window import ChildTopWindow
from foobnix.util.const import ICON_FOOBNIX
import logging
from foobnix.version import FOOBNIX_VERSION


class BaseParentWindow(ChildTopWindow):
    def __init__(self, title):
        ChildTopWindow.__init__(self, title)

        """ get foobnix icon path"""
        try:
            self.set_icon_from_file (self.get_fobnix_logo())
            gtk.window_set_default_icon_from_file (self.get_fobnix_logo())
        except TypeError: pass
            
    def get_fobnix_logo(self):
        return get_foobnix_resourse_path_by_name(ICON_FOOBNIX)

class AboutWindow(BaseParentWindow):
    """class About Window to show foobnix information"""

    def __init__(self):
        """init About window"""
        BaseParentWindow.__init__(self, _("About Window"))

        self.set_size_request(295, 210)

        """Content Begin"""
        table = gtk.Table(3, 4, False)
        try:
            pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(self.get_fobnix_logo(), 100, 100) #@UndefinedVariable
            image = gtk.image_new_from_pixbuf(pixbuf)
            #image = gtk.image_new_from_file(self.get_fobnix_logo())
            #image.set_pixel_size(10)
        except TypeError:
            image = gtk.image_new_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_INVALID)
        table.attach(image, 0, 3, 0, 1)
        url_label = gtk.LinkButton ("http://www.foobnix.com", "www.foobnix.com")
        url_label.set_relief(gtk.RELIEF_NONE)
        label = gtk.Label()
        label.set_markup ("\nFoobnix %s" % FOOBNIX_VERSION)
        
        label.set_justify(gtk.JUSTIFY_CENTER)
        table.attach(label, 0, 3, 1, 2)
        
        table.attach(url_label, 0, 3, 2, 3)

        label = gtk.Label("Credits")
        image = gtk.image_new_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)

        button_credits = self.create_button_with_label_and_icon(image, label)
        button_credits.set_border_width (9)
        table.attach(button_credits, 0, 1, 3, 4)

        label = gtk.Label(_("Close"))
        image = gtk.image_new_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU)

        button_close = self.create_button_with_label_and_icon(image, label)
        button_close.connect("clicked", self.hide_window)
        button_close.set_border_width (9)
        table.attach(button_close, 2, 3, 3, 4)

        label = gtk.Label(_("Changelog"))
        image = gtk.image_new_from_stock(gtk.STOCK_DND, gtk.ICON_SIZE_MENU)

        button_changelog = self.create_button_with_label_and_icon(image, label)
        button_changelog.set_border_width (9)
        table.attach(button_changelog, 1, 2, 3, 4)

        creaditsWindow = WindowWithBuffer(_("Credential"))

        text = """\t\t\tDevelopers:
    Ivan Ivanenko <ivan.ivanenko@gmail.com>
    Dmitry Kozhura (zavlab1) <zavlab1@gmail.com>"""

        creaditsWindow.set_text(text)

        changeLog = WindowWithBuffer("Change LOG")
        
        try:
            changelog_text = open(get_foobnix_resourse_path_by_name("CHANGELOG"), 'r').read()
            changeLog.set_text(changelog_text)
        except TypeError, error_message:
            logging.error(str(error_message))
            
        button_credits.connect("clicked", lambda * a: creaditsWindow.show_all())
        button_changelog.connect("clicked", lambda * x: changeLog.show_all())

        button_close.grab_focus ()
        self.add(table)


    def create_button_with_label_and_icon(self, image, label):
        box = gtk.HBox(False, 0)
        box.set_border_width (2)
        box.pack_end (label, True, False, 0)
        box.pack_end (image, True, False, 0)

        button = gtk.Button()
        button.add(box)
        return button


class WindowWithBuffer(BaseParentWindow):
    def __init__(self, title):
        BaseParentWindow.__init__(self, title)

        """init CreditsWindow"""
        self.set_size_request(500, 200)


        self.buffer = gtk.TextBuffer()

        text = gtk.TextView(self.buffer)
        text.set_editable(False)
        text.set_cursor_visible(False)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(text)

        self.add(scrolled_window)

    def set_text(self, text):
        self.buffer.set_text(text)

if __name__ == "__main__":
    w = AboutWindow()    
    w.show()
    gtk.main()







