# -*- coding: utf-8 -*-
'''
Created on Oct 2, 2010

@author: dimitry (zavlab1)
'''
import gtk
from foobnix.regui.service.image_service import get_foobnix_pixmap_path_by_name

class BaseParentWindow(gtk.Window):
    def __init__(self, title):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_position(gtk.WIN_POS_CENTER)        
        self.set_resizable(False)        
        self.set_title(title)
        
        """ get foobnix icon path"""                
        self.set_icon_from_file (self.get_fobnix_logo())
        
        self.connect("destroy", self.on_destroy)
        gtk.window_set_default_icon_from_file (get_foobnix_pixmap_path_by_name("foobnix.png"))    
    
    def get_fobnix_logo(self):
        return get_foobnix_pixmap_path_by_name("foobnix.png")
        
    def on_destroy(self,*a):
        self.hide()
        return True
    
"""class About Window to show foobnix information"""       
class AboutWindow(BaseParentWindow):
    def __init__(self):
        BaseParentWindow.__init__(self, "About Window")

        """init About window"""
        self.set_border_width(10)
        self.set_size_request(400,400)
    
    
        """Content Begin"""
        table = gtk.Table(3, 3, False)
            
        image = gtk.image_new_from_file(self.get_fobnix_logo());
        table.attach(image, 0, 3, 0, 1)
        
        label = gtk.Label("Foobnix")
        label.set_markup ("""
    <big><big><b><b>Foobnix</b></b></big></big>
    Playing all imaginations\n
    <small>Developed by Ivan Ivanenko</small>
    <small>ivan.ivanenko@gmail.com</small>\n   
    <a href="http://www.foobnix.com">www.foobnix.com</a>\n""");
        label.set_justify(gtk.JUSTIFY_CENTER)
        table.attach(label, 0, 3, 1, 2)
        
        label = gtk.Label("Credits")
        image = gtk.image_new_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        
        button_credits = self.create_button_with_label_and_icon(image,label)
        button_credits.set_border_width (9)
        table.attach(button_credits, 0, 1, 2, 3)
        
        label = gtk.Label("Close")
        image = gtk.image_new_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU)
        
        button_close = self.create_button_with_label_and_icon(image,label)
        button_close.connect("clicked", lambda *a: self.hide())
        button_close.set_border_width (9)
        table.attach(button_close, 2, 3, 2, 3)
        
        label = gtk.Label("Changelog")
        image = gtk.image_new_from_stock(gtk.STOCK_DND, gtk.ICON_SIZE_MENU)
        
        button_changelog = self.create_button_with_label_and_icon(image,label)
        button_changelog.set_border_width (9)
        table.attach(button_changelog, 1, 2, 2, 3)
        
        creaditsWindow = WindowWithBuffer("Credential")
        text = """\t\t\tDevelopers:
    Ivan Ivanenko <ivan.ivanenko@gmail.com>
    Anton Komolov <anton.komolov@gmail.com>
    Dmitry Kozhura <Dmitry-Kogura@yandex.ru>"""
    
        creaditsWindow.set_text(text)
        
        changeLog = WindowWithBuffer("Change LOG")
        changelog_text = """\t\t\tChangelog of Foobnix (since 2.0.9 version)\t\t"""
        changeLog.set_text(changelog_text)
        
        button_credits.connect("clicked", lambda *a: creaditsWindow.show_all())        
        button_changelog.connect("clicked", lambda * x:changeLog.show_all())
        
        button_close.grab_focus ()
        self.add(table)

    def create_button_with_label_and_icon(self, image,label): 
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
        self.set_border_width(10)
        self.set_size_request(300,300)
        
        
        self.buffer = gtk.TextBuffer()
        
        text=gtk.TextView(self.buffer)
        text.set_editable(False)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)       
        scrolled_window.add(text)
        
        self.add(scrolled_window)
        
    def set_text(self, text):
        self.buffer.set_text(text)
    
if __name__ == '__main__':
    about = AboutWindow()
    about.connect("destroy", lambda *a: gtk.main_quit())
    about.show_all()
    gtk.main()






