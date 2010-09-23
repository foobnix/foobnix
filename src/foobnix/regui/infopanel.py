'''
Created on Sep 23, 2010

@author: ivan
'''
import gtk
from foobnix.base.base_list_controller import BaseListController
from foobnix.util.mouse_utils import is_double_left_click
from foobnix.util import LOG
from foobnix.helpers.tree import ScrolledTreeView
class InfoPanelWidget():    
    def __init__(self): 
        info_frame = gtk.Frame()
        label = gtk.Label()
        label.set_markup("<b>Madonna - Album (2009)</b>")
        info_frame.set_label_widget(label)                                
        info_frame.set_shadow_type(gtk.SHADOW_NONE)
        
        paned = gtk.VPaned()
        
        """image and similar artists"""
        ibox = gtk.HBox(False, 0)
        image = gtk.Image()
        self.set_no_image_album(image)
        
        artists = ScrolledTreeView(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)        
        songsControll = SimilartArtistsController(artists)
        songsControll.set_title("Similar artists")
        
        ibox.pack_start(image, False, False)
        ibox.pack_start(artists.scroll, True, True)
        
        
        
        """image and similar artists"""
        sbox = gtk.HBox(False, 0)
        
        songs = ScrolledTreeView(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)        
        songsControll = SimilartArtistsController(songs)
        songsControll.set_title("Similar songs")
        
        
        tags = ScrolledTreeView(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        tagsControll = SimilartArtistsController(tags)
        tagsControll.set_title("Similar tags")
        
        sbox.pack_start(songs.scroll, True, True)
        sbox.pack_start(tags.scroll, True, True)
        
        
        
        paned.pack1(ibox, False, False)
        paned.pack2(sbox, True, True)
        
                
        info_frame.add(paned)
        

        
        info_frame.show_all()
               
        self.widget = info_frame
    
    def set_no_image_album(self, image):
      
        image_name = "blank-disc-cut.jpg"
        
        try:
            pix = gtk.gdk.pixbuf_new_from_file("/usr/local/share/pixmaps/" + image_name) #@UndefinedVariable
        except:
            try:
                pix = gtk.gdk.pixbuf_new_from_file("/usr/share/pixmaps/" + image_name) #@UndefinedVariable
            except:    
                pix = gtk.gdk.pixbuf_new_from_file("foobnix/pixmaps/" + image_name) #@UndefinedVariable

        pix = pix.scale_simple(100, 100, gtk.gdk.INTERP_BILINEAR) #@UndefinedVariable
        image.set_from_pixbuf(pix)
        
        
        
class SimilartArtistsController(BaseListController):
    def __init__(self, widget):
        BaseListController.__init__(self, widget)
    
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            artist = self.get_selected_item()
            LOG.debug("Clicked Similar Artist:", artist)            
