import gtk
from foobnix.regui.service.image_service import get_foobnix_pixmap_path_by_name


def credits():
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title ("Credits")
    print "Credits, every time I am creating new instance of Credits when open it."
    window.set_position(gtk.WIN_POS_CENTER)
    window.set_border_width(10)
    #window.set_default_size(500,200)
    window.set_size_request(500, 200)
    gtk.window_set_default_icon_from_file (get_foobnix_pixmap_path_by_name("foobnix.png"))
    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
    
    window.connect("destroy", lambda * x:window.hide())
    
    buffer=gtk.TextBuffer()
    buffer_content="""\t\t\tDevelopers:
Ivan Ivanenko <ivan.ivanenko@gmail.com>
Anton Komolov <anton.komolov@gmail.com>
Dmitry Kozhura <Dmitry-Kogura@yandex.ru>"""
    buffer.set_text(buffer_content)
    text=gtk.TextView(buffer)
    text.set_editable(False)
    text.set_cursor_visible(False)
    scrolled_window.add(text)
    
    button=gtk.Button("Close",gtk.STOCK_CLOSE)
    
    
    button.connect("clicked", lambda * x:window.hide())
    
    hbox=gtk.HBox(True, 0)
    hbox.pack_start (button, False, False, 0)
    
    vbox=gtk.VBox(False, 10)
    vbox.pack_start (scrolled_window, True, True, 0)
    vbox.pack_start (hbox, False, False, 0)
    
    button.grab_focus ()
    window.add(vbox)
    window.show_all()
    
    

    