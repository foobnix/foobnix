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
from foobnix.model.entity import CommonBean
class InfortaionController():
    def __init__(self,gx_main, last_fm_network):
        self.album_image = gx_main.get_widget("image_widget")
        
        """album name"""
        self.album_name = gx_main.get_widget("label_album_name")        
        self.album_name.set_use_markup(gtk.TRUE)
        
        self.current_song_label = gx_main.get_widget("current_song_label")
        self.current_song_label.set_use_markup(gtk.TRUE)
        """Similar artists"""
        self.similar_artists = gx_main.get_widget("treeview_similart_artists")        
        self.similar_artists_model = gtk.ListStore(str)
        song_column = gtk.TreeViewColumn(_('Similar Artists'), gtk.CellRendererText(), text=0)
        self.similar_artists.append_column(song_column)        
        self.similar_artists.set_model(self.similar_artists_model)
        
        """similar songs"""
        self.similar_songs = gx_main.get_widget("treeview_similar_songs")
        self.similar_songs_model = gtk.ListStore(str, str)
        song_column = gtk.TreeViewColumn(_('Similar songs'), gtk.CellRendererText(), text=0)
        self.similar_songs.append_column(song_column)        
        self.similar_songs.set_model(self.similar_songs_model)
        
        """song tags"""       
        self.song_tags = gx_main.get_widget("treeview_song_tags")
        self.song_tags_model = gtk.ListStore(str)
        song_column = gtk.TreeViewColumn(_('Song tags'), gtk.CellRendererText(), text=0)
        self.song_tags.append_column(song_column)        
        self.song_tags.set_model(self.song_tags_model)
        
        
        
        self.last_fm_network = last_fm_network
    
    def add_similar_song(self, song):
        self.similar_songs_model.append([song.get_short_description(), song.path])
    
    def add_similar_artist(self, artist):
        self.similar_artists_model.append([artist])
    
    def add_tag(self, tag):
        self.song_tags_model.append([tag])
    
    def show_song_info(self, song):
        thread.start_new_thread(self.show_song_info_tread, (song,))
        #self.show_song_info_tread(song)
            
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
        
        self.current_song_label.set_markup("<b>" + song.getTitle()+"</b>")
        
        track = self.last_fm_network.get_track(song.getArtist(), song.getTitle())        
        #album = self.last_fm_network.get_album(song.getArtist(), song.getTitle())
        album = track.get_album()
        
        """similar tracks"""
        similars = track.get_similar()
        self.similar_songs_model.clear()
        for tsong in similars:
            try:            
                tsong_item = tsong.item
            except AttributeError:
                tsong_item = tsong['item']
            
            
            tsong = CommonBean(name=str(tsong_item), type=CommonBean.TYPE_MUSIC_URL)
            self.add_similar_song(tsong)
        
        """similar tags"""
        tags = track.get_top_tags(20)        
        self.song_tags_model.clear()
        for tag in tags:
            try:            
                tag_item = tag.item
            except AttributeError:
                tag_item = tag['item']
            self.add_tag(tag_item.get_name())
        
        """similar artists"""
        artist = track.get_artist()
        similar_artists = artist.get_similar(30)
       
        self.similar_artists_model.clear()
        for artist in similar_artists:
            try:            
                artist_item = artist.item
            except AttributeError:
                artist_item = artist['item']
            self.add_similar_artist(artist_item.get_name())
        
        LOG.info("Find album", album)
        if not album:
            return None
        LOG.info(album)
        try:
            image = album.get_cover_image(size=pylast.COVER_EXTRA_LARGE)
        except:            
            LOG.info("image not found for:", song)
        
        self.album_name.set_markup("<b>" +song.getArtist() + " - " +  album.get_name()+"</b>")
        
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
 
        
