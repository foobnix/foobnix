'''
Created on Sep 28, 2010

@author: ivan
'''
import gtk
from foobnix.util.pix_buffer import create_pixbuf_from_resource, \
    create_pixbuf_from_url, create_pixbuf_from_path, resize_pixbuf
import logging
import os

class ImageBase(gtk.Image):
    def __init__(self, resource, size=None):
        gtk.Image.__init__(self)
        self.pixbuf = None
        self.resource = resource
        self.size = size
        self.set_no_image()
        
    def set_no_image(self):
        self.pixbuf = create_pixbuf_from_resource(self.resource, self.size)
        self.set_from_pixbuf(self.pixbuf)
        
    def set_from_resource(self, resource_name):
        self.pixbuf = create_pixbuf_from_resource(resource_name, self.size)
        self.set_from_pixbuf(self.pixbuf)

    
    def set_from_pixbuf(self, pix):
        self.pixbuf = resize_pixbuf(pix, self.size)
        super(ImageBase, self).set_from_pixbuf(self.pixbuf)
        
        
    def set_image_from_url(self, url):
        self.pixbuf = create_pixbuf_from_url(url, self.size)
        self.set_from_pixbuf(self.pixbuf)
    
    def set_image_from_path(self, path):
        if not os.path.isfile(path):
            return self.set_from_resource(path)
        
        logging.debug("Change icon path %s" % path)
        self.pixbuf = create_pixbuf_from_path(path, self.size)
        self.set_from_pixbuf(self.pixbuf)
    
    def get_pixbuf(self):
        return self.pixbuf
        
    def update_info_from(self, bean):
        if not bean or not bean.image:
            self.set_no_image() 
            return
        if bean.image.startswith("http://"):
            self.set_image_from_url(bean.image)
        else:
            self.set_image_from_path(bean.image)
