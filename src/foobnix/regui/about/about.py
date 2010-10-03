'''
Created on Oct 2, 2010

@author: dimitry (zavlab1)
'''
import gtk
from foobnix.regui.service.image_service import get_foobnix_pixmap_path_by_name

def about():
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title ("About Foobnix")
    window.set_position(gtk.WIN_POS_CENTER)
    window.set_border_width(10)
    window.set_geometry_hints(window, min_width=270, min_height=300)
    gtk.window_set_default_icon_from_file ("/usr/share/pixmaps/foobnix.png")
    window.set_resizable(False)
    
    """ get foobnix icon path"""
    foobnix_image_path = get_foobnix_pixmap_path_by_name("foobnix.png")
    
    window.set_icon_from_file (foobnix_image_path)
    
    table = gtk.Table(2, 3, False)
    table.set_col_spacing(0, 50)
    
    image = gtk.image_new_from_file(foobnix_image_path);
    table.attach(image, 0, 2, 0, 1)
    
    label = gtk.Label("Foobnix")
    
    label.set_markup ("""
    <big><big><b><b>Foobnix</b></b></big></big>
    Playing all imaginations\n
    <small>Developed by Ivan Ivanenko</small>
    <small>ivan.ivanenko@gmail.com</small>\n   
    <a href="www.foobnix.com">www.foobnix.com</a>
    """);
    
    label.set_justify(gtk.JUSTIFY_CENTER)
    table.attach(label, 0, 2, 1, 2)
    
    label = gtk.Label("Credits")
    image = gtk.image_new_from_stock(gtk.STOCK_INFO,2)
    
    box = gtk.HBox(False, 0)
    box.set_border_width (2)
    box.pack_end (label, True, False, 0)
    box.pack_end (image, True, False, 0)
    
    button = gtk.Button()
    button.set_border_width (5)
    button.add(box)
    table.attach(button, 0, 1, 2, 3)
    
    label = gtk.Label("Close")
    image = gtk.image_new_from_stock(gtk.STOCK_STOP,2)
    
    box = gtk.HBox(False, 0)
    box.set_border_width (2)
    box.pack_end (label, True, False, 0)
    box.pack_end (image, True, False, 0)
    
    button = gtk.Button()
    button.set_border_width (5)
    button.add(box)
    table.attach(button, 1, 2, 2, 3)
    
    window.connect("destroy", lambda * x:gtk.main_quit())
    button.connect("clicked", lambda * x:gtk.main_quit())
    button.grab_focus ()
    window.add(table)
    window.show_all()
    


about()
gtk.main()

