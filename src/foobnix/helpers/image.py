'''
Created on Sep 28, 2010

@author: ivan
'''
import gtk
from foobnix.util.pix_buffer import create_pixbuf_from_resource,\
    create_pixbuf_from_url, create_pixbuf_from_path, resize_pixbuf
from foobnix.util.fc import FC
import gobject

class ImageBase(gtk.Image):
    def __init__(self, resource, size=None):
        gtk.Image.__init__(self)
        self.pixbuf = None
        self.resource = resource
        self.size = size
        self.set_no_image()
        
    def set_no_image(self, size=None):
        self.pixbuf = create_pixbuf_from_resource(self.resource, size)
        self.set_from_pixbuf(self.pixbuf)
    
    def set_from_pixbuf(self,pix):
        self.pixbuf = resize_pixbuf(pix, FC().info_panel_image_size)
        def task():
            super(ImageBase, self).set_from_pixbuf(self.pixbuf)
        gobject.idle_add(task)
        
    def set_image_from_url(self, url, size=None):
        self.pixbuf = create_pixbuf_from_url(url, size)
        self.set_from_pixbuf(self.pixbuf)
    
    def set_image_from_path(self, path, size):
        self.pixbuf = create_pixbuf_from_path(path, size)
        self.set_from_pixbuf(self.pixbuf)
    
    def get_pixbuf(self):
        self.pixbuf
        
    def update_info_from(self, bean):
        if not bean or not bean.image:
            self.set_no_image(self.size) 
            return
        if bean.image.startswith("http://"):
            self.set_image_from_url(bean.image, self.size)
        else:
            self.set_image_from_path(bean.image, self.size)