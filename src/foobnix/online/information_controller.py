'''
Created on 18.04.2010

@author: ivan
'''
from foobnix.util import LOG
from foobnix.online.pylast import COVER_MEDIUM
from foobnix.online import pylast
import urllib
import gtk
import thread
class InfortaionController():
    def __init__(self,gx_main, last_fm_network):
        self.album_image = gx_main.get_widget("image_widget")
        self.similar_artists = gx_main.get_widget("treeview_similart_artists")
        self.biography_textVeiw = gx_main.get_widget("biography_textview")
        self.similar_artists = gx_main.get_widget("treeview_similar_songs")
        self.song_tags = gx_main.get_widget("treeview_song_tags")
        
        self.last_fm_network = last_fm_network
    
    def show_song_info(self, song):
        thread.start_new_thread(self.show_song_info_tread, (song,))
            
    def show_song_info_tread(self, song):
        self.song = song
        LOG.info("Get all possible information about song")
        image_url = self.get_album_image_url(song)        
        if not image_url:
            LOG.info("Image not found, load empty.")
            return None
    
        image_pix_buf = self.create_pbuf_image_from_url(image_url)
        self.album_image.set_from_pixbuf(image_pix_buf)
    
    def set_image(self, path):
        pass
    
    def get_album_image_url(self, song):
        album = self.last_fm_network.get_album(song.getArtist(), song.getTitle())
        LOG.info("Find album", album)
        if not album:
            return None
        LOG.info(album)
        try:
            image = album.get_cover_image(size=pylast.COVER_EXTRA_LARGE)
        except:
            LOG.info("image not found for:", song)
            
        LOG.info("image:", image)        
        return image
    
    def create_pbuf_image_from_url(self, url_to_image):
        f = urllib.urlopen(url_to_image)
        data = f.read()
        pbl = gtk.gdk.PixbufLoader() #@UndefinedVariable
        pbl.write(data)
        pbuf = pbl.get_pixbuf()
        pbl.close()
        return pbuf   
 
        
