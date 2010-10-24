# -*- coding: utf-8 -*-
'''
Created on Oct 2, 2010

@author: dimitry (zavlab1)
'''

import gtk
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name


class BaseParentWindow(gtk.Window):
    def __init__(self, title):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_resizable(False)
        self.set_title(title)
        self.set_border_width(10)

        """ get foobnix icon path"""
        self.set_icon_from_file (self.get_fobnix_logo())

        self.connect("destroy", self.on_destroy)
        gtk.window_set_default_icon_from_file (self.get_fobnix_logo())
        self.connect("delete-event", lambda * a: self.on_destroy())
        self.connect("destroy", lambda * a: self.on_destroy())
        self.connect("key_press_event", self.key_press_event)
        
    def get_fobnix_logo(self):
        return get_foobnix_resourse_path_by_name("foobnix.png")

    def on_destroy(self, *a):
        self.hide()
        return True
    
    '''Closing of window on Escape'''
    def key_press_event(self, widget, event):
        if event.keyval == gtk.keysyms.Escape:
            self.hide()
        return True

class AboutWindow(BaseParentWindow):
    """class About Window to show foobnix information"""

    def __init__(self):
        """init About window"""
        BaseParentWindow.__init__(self, "About Window")

        self.set_size_request(320, 275)

        """Content Begin"""
        table = gtk.Table(3, 3, False)

        image = gtk.image_new_from_file(self.get_fobnix_logo());
        table.attach(image, 0, 3, 0, 1)

        label = gtk.Label("Foobnix")
        label.set_markup ("""<big><big><b><b>Foobnix</b></b></big></big>
Playing all imaginations\n
<small>Developed by Ivan Ivanenko</small>
<small>ivan.ivanenko@gmail.com</small>\n
<a href="http://www.foobnix.com">www.foobnix.com</a>\n""")
        label.set_justify(gtk.JUSTIFY_CENTER)
        table.attach(label, 0, 3, 1, 2)

        label = gtk.Label("Credits")
        image = gtk.image_new_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)

        button_credits = self.create_button_with_label_and_icon(image, label)
        button_credits.set_border_width (9)
        table.attach(button_credits, 0, 1, 2, 3)

        label = gtk.Label("Close")
        image = gtk.image_new_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU)

        button_close = self.create_button_with_label_and_icon(image, label)
        button_close.connect("clicked", lambda * a: self.on_destroy())
        button_close.set_border_width (9)
        table.attach(button_close, 2, 3, 2, 3)

        label = gtk.Label("Changelog")
        image = gtk.image_new_from_stock(gtk.STOCK_DND, gtk.ICON_SIZE_MENU)

        button_changelog = self.create_button_with_label_and_icon(image, label)
        button_changelog.set_border_width (9)
        table.attach(button_changelog, 1, 2, 2, 3)

        creaditsWindow = WindowWithBuffer("Credential")

        text = """\t\t\tDevelopers:
    Ivan Ivanenko <ivan.ivanenko@gmail.com>
    Anton Komolov <anton.komolov@gmail.com>
    Dmitry Kozhura <Dmitry-Kogura@yandex.ru>"""

        creaditsWindow.set_text(text)

        changeLog = WindowWithBuffer("Change LOG")
        
        try:
            changelog_text = open(get_foobnix_resourse_path_by_name("CHANGELOG"), 'r').read()
            changeLog.set_text(changelog_text)
        except TypeError, error_message:
            print error_message
          
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

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(text)

        self.add(scrolled_window)

    def set_text(self, text):
        self.buffer.set_text(text)









