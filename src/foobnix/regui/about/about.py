'''
Created on Oct 2, 2010

@author: dimitry
'''
import gtk

def close_application( widget,event,gpointer ): 
    gtk.main_quit()
    return False

def about():
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title ("About Foobnix")
    window.set_position(gtk.WIN_POS_CENTER)
    window.set_border_width(10)
    window.set_default_size(250, 200) 
    window.set_icon_from_file ("/usr/share/pixmaps/foobnix.png")
    
    table = gtk.Table(2, 3, False)
    table.set_col_spacing(0, 50)
    
    image = gtk.image_new_from_file("/usr/share/pixmaps/foobnix.png");
    table.attach(image, 0, 2, 0, 1)
    
    label = gtk.Label( "Foobnix" )
    label.set_markup ("\n<big><big><b><b>Foobnix\n</b></b></big></big>\nPlaying all imaginations\n\n<small>Developed by Ivan Ivanenko\nivan.ivanenko@gmail.com\n\n</small><a href=\"http://code.google.com/p/foobnix/\">Page of development</a>\n");
    label.set_justify(gtk.JUSTIFY_CENTER)
    table.attach(label, 0, 2, 1, 2)
    
    label = gtk.Label("Credits")
    image = gtk.image_new_from_file ("/usr/share/icons/oxygen/16x16/actions/help-about.png")
    
    box = gtk.HBox(False, 0)
    box.set_border_width (2)
    box.pack_end (label,  True, False, 0)
    box.pack_end (image,  True, False, 0)
    
    button = gtk.Button()
    button.add(box)
    table.attach(button, 0, 1, 2, 3)
    
    label = gtk.Label("Close")
    image = gtk.image_new_from_file ("/usr/share/icons/oxygen/16x16/actions/dialog-close.png")
    
    box = gtk.HBox(False, 0)
    box.set_border_width (2)
    box.pack_end (label,  True, False, 0)
    box.pack_end (image,  True, False, 0)
    button = gtk.Button()
    button.add(box)
    table.attach(button, 1, 2, 2, 3)
    
    window.connect("destroy", lambda *a:gtk.main_quit())
    button.connect("clicked", lambda *a:gtk.main_quit())
    button.grab_focus ()
    window.add(table)
    window.show_all()
    gtk.main()
    
about()