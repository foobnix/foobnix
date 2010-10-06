# -*- coding: utf-8 -*-
'''
Created on Oct 2, 2010

@author: dimitry (zavlab1)
'''
import gtk
from foobnix.regui.service.image_service import get_foobnix_pixmap_path_by_name


class BaseParentWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.set_position(gtk.WIN_POS_CENTER)        
        self.set_resizable(False)
        self.connect("destroy", self.on_destroy)
        gtk.window_set_default_icon_from_file (get_foobnix_pixmap_path_by_name("foobnix.png"))
            
    def on_destroy(self,*a):
        self.hide()
        return True
        
    def add_content(self, content):
        self.add(content)

       
class AboutWindow(BaseParentWindow):
    def __init__(self, title, border_width, width_window, high_window):
        BaseParentWindow.__init__(self)
        self.set_title(title)
        self.set_border_width(border_width)
        self.set_size_request(width_window, high_window)
               
        
class Window_with_Scrollbars (AboutWindow, gtk.TextBuffer):
       
    def __init__(self, title, border_width, width_window, high_window, buffer_content):
        AboutWindow.__init__(self, title, border_width, width_window, high_window)
        gtk.TextBuffer.__init__(self)
        self.buffer = gtk.TextBuffer()
        self.buffer.set_text(buffer_content)
        self.text=gtk.TextView(self.buffer)
        self.text.set_editable(False)
        #self.text.set_cursor_visible(False)
        self.scrolled_window = gtk.ScrolledWindow()
        self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        self.scrolled_window.add(self.text)
        self.scrolled_window.show()
        

def create_button_with_label_and_icon(image,label): 
    box = gtk.HBox(False, 0)
    box.set_border_width (2)
    box.pack_end (label, True, False, 0)
    box.pack_end (image, True, False, 0)
    
    button = gtk.Button()
    button.add(box)
    return button        
        
   
def about():
    
    window = AboutWindow("About Foobnix", 5, 310, 270)
    
    """ get foobnix icon path"""
    foobnix_image_path = get_foobnix_pixmap_path_by_name("foobnix.png")
    
    window.set_icon_from_file (foobnix_image_path)
    
    table = gtk.Table(3, 3, False)
        
    image = gtk.image_new_from_file(foobnix_image_path);
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
    
    button_credits = create_button_with_label_and_icon(image,label)
    button_credits.set_border_width (9)
    table.attach(button_credits, 0, 1, 2, 3)
    
    label = gtk.Label("Close")
    image = gtk.image_new_from_stock(gtk.STOCK_STOP, gtk.ICON_SIZE_MENU)
    
    button_close = create_button_with_label_and_icon(image,label)
    button_close.set_border_width (9)
    table.attach(button_close, 2, 3, 2, 3)
    
    label = gtk.Label("Changelog")
    image = gtk.image_new_from_stock(gtk.STOCK_DND, gtk.ICON_SIZE_MENU)
    
    button_changelog = create_button_with_label_and_icon(image,label)
    button_changelog.set_border_width (9)
    table.attach(button_changelog, 1, 2, 2, 3)
    
    buffer_content_credits = """\t\t\tDevelopers:
Ivan Ivanenko <ivan.ivanenko@gmail.com>
Anton Komolov <anton.komolov@gmail.com>
Dmitry Kozhura <Dmitry-Kogura@yandex.ru>"""
    
    buffer_content_changelog = """\t\t\tChangelog of Foobnix (since 2.0.9 version)\t\t"""
    
    window.connect("destroy", lambda * x:window.on_destroy())
    button_close.connect("clicked", lambda * x:window.on_destroy())
    button_credits.connect("clicked", lambda * x:credits_and_changelog (buffer_content_credits, "Credits"))
    button_changelog.connect("clicked", lambda * x:credits_and_changelog (buffer_content_changelog, "Changelog"))
    
    button_close.grab_focus ()
    window.add_content(table)
    window.show_all()
    

def credits_and_changelog (buffer_content, title):
    
    window = Window_with_Scrollbars (title, 10, 500, 200, buffer_content)
    window.connect("destroy", lambda * x:window.hide())
        
    button=gtk.Button("Close", gtk.STOCK_CLOSE)
    button.connect("clicked", lambda * x:window.hide())
    
    hbox=gtk.HBox(True, 0)
    hbox.pack_start (button, False, False, 0)
    
    vbox=gtk.VBox(False, 10)
    vbox.pack_start (window.scrolled_window, True, True, 0)
    vbox.pack_start (hbox, False, False, 0)
    
    button.grab_focus ()
    window.add(vbox)
    window.show_all()
    
    
if __name__ == '__main__':
    about()
    gtk.main()






