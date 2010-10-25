'''
Created on Sep 28, 2010

@author: ivan
'''
import gtk
import urllib
from foobnix.util import LOG
class CoverImage(gtk.Image):
    def __init__(self, size=150):
        gtk.Image.__init__(self)
        self.size = size
        self.set_no_image()
        
    def set_no_image(self):
        image_name = "blank-disc-cut.jpg"
        
        try:
            pix = gtk.gdk.pixbuf_new_from_file("/usr/local/share/pixmaps/" + image_name) #@UndefinedVariable
        except:
            try:
                pix = gtk.gdk.pixbuf_new_from_file("/usr/share/pixmaps/" + image_name) #@UndefinedVariable
            except:    
                pix = gtk.gdk.pixbuf_new_from_file("foobnix/pixmaps/" + image_name) #@UndefinedVariable
        
        pix = pix.scale_simple(self.size, self.size, gtk.gdk.INTERP_BILINEAR) #@UndefinedVariable
        self.set_from_pixbuf(pix)
        
    def set_image_from_url(self, url):
        if not url:
            LOG.warn("set_image_from_url URL is empty")
            return None
        image = self._create_pbuf_image_from_url(url)
        image_pix_buf = image.scale_simple(self.size, self.size, gtk.gdk.INTERP_BILINEAR) #@UndefinedVariable
        self.set_from_pixbuf(image_pix_buf)
    
    def set_image_from_path(self, path):
        pixbuf = gtk.gdk.pixbuf_new_from_file(path) #@UndefinedVariable
        scaled_buf = pixbuf.scale_simple(self.size, self.size, gtk.gdk.INTERP_BILINEAR) #@UndefinedVariable
        self.set_from_pixbuf(scaled_buf)
    
    
    def _create_pbuf_image_from_url(self, url_to_image):
        f = urllib.urlopen(url_to_image)
        data = f.read()
        pbl = gtk.gdk.PixbufLoader() #@UndefinedVariable
        pbl.write(data)
        pbuf = pbl.get_pixbuf()
        pbl.close()
        return pbuf   