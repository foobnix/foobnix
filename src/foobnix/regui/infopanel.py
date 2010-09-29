'''
Created on Sep 23, 2010

@author: ivan
'''
import gtk
from foobnix.regui.state import LoadSave
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl
from foobnix.regui.treeview.simple import SimpleTreeControl
from foobnix.helpers.image import CoverImage

class InfoPanelWidget(gtk.Frame, LoadSave, FControl):    
    def __init__(self, controls): 
        gtk.Frame.__init__(self)
        FControl.__init__(self, controls)
        self.almum_label = gtk.Label()
        self.almum_label.set_line_wrap(True)
        self.almum_label.set_markup("<b></b>")
        self.set_label_widget(self.almum_label)                                
        self.set_shadow_type(gtk.SHADOW_NONE)
        
        self.vpaned_small = gtk.VPaned()
        
        """image and similar artists"""
        ibox = gtk.HBox(False, 0)
        self.image = CoverImage()
        
        self.artists = SimpleTreeControl("Similar Artist", controls).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)  
        
        ibox.pack_start(self.image, False, False)
        ibox.pack_start(self.artists.scroll, True, True)
        
        
        
        """image and similar artists"""
        sbox = gtk.HBox(False, 0)
        
        self.tracks = SimpleTreeControl("Similar Songs", controls).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        self.tags = SimpleTreeControl("Similar Tags", controls).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)      
        
        sbox.pack_start(self.tracks.scroll, True, True)
        sbox.pack_start(self.tags.scroll, True, True)
        
        
        
        self.vpaned_small.pack1(ibox, False, False)
        self.vpaned_small.pack2(sbox, True, True)
        
                
        self.add(self.vpaned_small)
        
        self.show_all()

    def update(self, bean):
        #return
        print "update info panel", bean
        
        """update info"""
        album_name = self.controls.lastfm.get_album_name(bean.artist, bean.title)
        album_year = self.controls.lastfm.get_album_year(bean.artist, bean.title)
        if album_year:
            self.almum_label.set_markup("<b>%s - %s (%s) - %s</b>" % (bean.artist, album_name, album_year, bean.title))
        else:
            self.almum_label.set_markup("<b>%s - %s - %s</b>" % (bean.artist, album_name, bean.title))
        
        """update image"""
        if bean.image:
            self.image.set_image_from_path(bean.image)
        else:
            url = self.controls.lastfm.get_album_image_url(bean.artist, bean.title)
            if url:
                self.image.set_image_from_url(url)
            else:
                self.image.set_no_image()
            
        """similar  artists"""
        similar_artists = self.controls.lastfm.search_top_similar_artist(bean.artist)        
        self.artists.populate(similar_artists)
        
        """similar  songs"""
        similar_tracks = self.controls.lastfm.search_top_similar_tracks(bean.artist, bean.title)
        self.tracks.populate(similar_tracks)
        
        """similar  tags"""
        similar_tags = self.controls.lastfm.search_top_similar_tags(bean.artist, bean.title)
        self.tags.populate(similar_tags)       
    
     
    def on_load(self):
        self.vpaned_small.set_position(FC().vpaned_small) 
         
    def on_save(self):
        FC().vpaned_small = self.vpaned_small.get_position()    
