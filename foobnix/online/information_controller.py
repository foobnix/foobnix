'''
Created on 18.04.2010

@author: ivan
'''
from foobnix.util import LOG
from foobnix.thirdparty import pylast
import urllib
import gtk
import thread
from foobnix.model.entity import CommonBean
from foobnix.base.base_list_controller import BaseListController
from foobnix.online.song_resource import SongResource

class SimilartSongsController(BaseListController):
        def __init__(self, gx_main, playerCntr, directoryCntr):
            self.directoryCntr = directoryCntr
            self.playerCntr = playerCntr
            widget = gx_main.get_widget("treeview_similar_songs")
            BaseListController.__init__(self, widget)
            
        def on_duble_click(self):
            artist_track = self.get_selected_item()
            song = CommonBean(name=artist_track, type=CommonBean.TYPE_MUSIC_URL)
            resource = SongResource()
            song.path = resource.get_song_path(song)
            self.playerCntr.playSong(song)
        
        def on_drag(self):
            items = self.get_all_items()
            songs = []
            parent = "Similar songs"
            song = CommonBean(name=parent, type=CommonBean.TYPE_FOLDER)
            songs.append(song)
            for item in items:                
                song = CommonBean(name=item, type=CommonBean.TYPE_MUSIC_URL, parent=parent)
                songs.append(song)
            self.directoryCntr.append_virtual(songs)
        

class InformationController():
    def __init__(self,gx_main, last_fm_network, playerCntr, directoryCntr):
        
        self.album_image = gx_main.get_widget("image_widget")
        
        """album name"""
        self.album_name = gx_main.get_widget("label_album_name")        
        self.album_name.set_use_markup(True)
        
        self.current_song_label = gx_main.get_widget("current_song_label")
        self.current_song_label.set_use_markup(gtk.TRUE)
        
        """Similar artists"""
        self.similar_artists = gx_main.get_widget("treeview_similart_artists")        
        self.similar_artists_model = gtk.ListStore(str)
        song_column = gtk.TreeViewColumn(_('Similar Artists'), gtk.CellRendererText(), text=0)
        self.similar_artists.append_column(song_column)        
        self.similar_artists.set_model(self.similar_artists_model)
        
        """similar songs"""
        self.similar_songs_cntr = SimilartSongsController(gx_main, playerCntr, directoryCntr)              
        self.similar_songs_cntr.set_title("Similar Songs")   
        
        """song tags"""       
        self.song_tags = gx_main.get_widget("treeview_song_tags")
        self.song_tags_model = gtk.ListStore(str)
        song_column = gtk.TreeViewColumn(_('Song tags'), gtk.CellRendererText(), text=0)
        self.song_tags.append_column(song_column)        
        self.song_tags.set_model(self.song_tags_model)
        
        
        self.last_album_name = None
        
        self.last_fm_network = last_fm_network
    
    def show_song_info(self, song):
        thread.start_new_thread(self.show_song_info_tread, (song,))
        #self.show_song_info_tread(song)
    
    def add_similar_song(self, song):
        self.similar_songs_model.append([song.get_short_description(), song.path])
        #self.similar_songs_cntr.add_item(song.get_name())
    
    def add_similar_artist(self, artist):
        self.similar_artists_model.append([artist])
    
    def add_tag(self, tag):
        self.song_tags_model.append([tag])
    
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
        print track
        if not track:
            return None
        
        """similar tracks"""
        try:
            similars = track.get_similar()
        except:
            LOG.error("Similar not found")
            return None
            
        self.similar_songs_cntr.clear()
        for tsong in similars:
            try:            
                tsong_item = tsong.item
            except AttributeError:
                tsong_item = tsong['item']
            #tsong = CommonBean(name=str(tsong_item), type=CommonBean.TYPE_MUSIC_URL)
            self.similar_songs_cntr.add_item(str(tsong_item))
        
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
        
        album = track.get_album()
        if album:
            self.album_name.set_markup("<b>" +song.getArtist() + " - " +  album.get_name()+"</b>")
        
                
        #album = self.last_fm_network.get_album(song.getArtist(), song.getTitle())
        
        
        if not album:
            return None
        
        
       
        
        LOG.info("Find album", album)
        
        if self.last_album_name == album.get_name():
            LOG.info("Album the same, not need to dowlaod image")
            #TODO  need to implement album image cache
            return None
        
        if not album:
            return None
        LOG.info(album)
        try:
            image = album.get_cover_image(size=pylast.COVER_EXTRA_LARGE)
            self.last_album_name = album.get_name()
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
 
        
