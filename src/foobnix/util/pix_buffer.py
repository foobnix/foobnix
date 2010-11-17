'''
Created on Nov 4, 2010

@author: ivan
'''
import urllib
from foobnix.regui.service.path_service import get_foobnix_resourse_path_by_name
import gtk

def create_pixbuf_from_url(url, size):
    pixbuf = create_origin_pixbuf_from_url(url)
    if size:
        return resize_pixbuf(pixbuf, size)
    else:
        return pixbuf

def resize_pixbuf(pixbuf, size):
    if not pixbuf:
        return None
    if size:
        return pixbuf.scale_simple(size, size, gtk.gdk.INTERP_BILINEAR) #@UndefinedVariable
    else:
        return pixbuf

def create_pixbuf_from_path(path, size):
    try:
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
    except Exception, e:
        print e
        return None
    
    if size:
        return resize_pixbuf(pixbuf, size)
    else:
        return pixbuf

def create_pixbuf_from_resource(name, size):
    path = get_foobnix_resourse_path_by_name(name);
    return create_pixbuf_from_path(path, size)

def create_origin_pixbuf_from_url(url):
    f = urllib.urlopen(url)
    data = f.read()
    pbl = gtk.gdk.PixbufLoader() #@UndefinedVariable
    pbl.write(data)
    pbuf = pbl.get_pixbuf()
    pbl.close()
    return pbuf   
