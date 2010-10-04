import gtk
import pango
from foobnix.regui.service.image_service import get_foobnix_pixmap_path_by_name

def changelog():
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.set_title ("Changelog")
    window.set_position(gtk.WIN_POS_CENTER)
    window.set_border_width(10)
    window.set_size_request(500, 200)
    gtk.window_set_default_icon_from_file (get_foobnix_pixmap_path_by_name("foobnix.png"))
    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    window.set_resizable(False)
    
    window.connect("destroy", lambda * x:window.hide())
    
    bold_tag = gtk.TextTag("bold")
    
    """this is fix"""
    bold_tag.set_property("weight", pango.WEIGHT_BOLD)
    bold_tag.set_property("background", "#FFAA33")
    
    texttagtable = gtk.TextTagTable()
    texttagtable.add (bold_tag)
    buffer = gtk.TextBuffer(texttagtable)
    buffer_content = """\t\tChangelog of Foobnix (since 2.0.9 version)\t\t"""
    buffer.set_text(buffer_content)
    buffer.apply_tag(bold_tag, buffer.get_start_iter(), buffer.get_end_iter())
    
    text = gtk.TextView(buffer)
    text.set_editable(False)
    text.set_cursor_visible(False)
    scrolled_window.add(text)
    button = gtk.Button("Close", gtk.STOCK_CLOSE)
    
    button.connect("clicked", lambda * x:window.hide())
    
    hbox = gtk.HBox(True, 0)
    hbox.pack_start (button, False, False, 0)
    
    vbox = gtk.VBox(False, 10)
    vbox.pack_start (scrolled_window, True, True, 0)
    
    vbox.pack_start (hbox, False, False, 0)
    button.grab_focus ()
    
    window.add(vbox)
    window.show_all()
    

if __name__ == '__main__':
    changelog()    
    gtk.main()
    
