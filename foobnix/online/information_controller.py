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
from foobnix.util.configuration import FConfiguration
import datetime
import time
from foobnix.online.song_resource import update_song_path


class SimilartSongsController(BaseListController):
        def __init__(self, gx_main, playerCntr, directoryCntr):
            self.directoryCntr = directoryCntr
            self.playerCntr = playerCntr
            widget = gx_main.get_widget("treeview_similar_songs")
            BaseListController.__init__(self, widget)
            
        def on_duble_click(self):
            artist_track = self.get_selected_item()
            song = CommonBean(name=artist_track, type=CommonBean.TYPE_MUSIC_URL)
            update_song_path(song)
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

class SimilartArtistsController(BaseListController):
    def __init__(self, gx_main, search_panel):
        self.search_panel = search_panel
        widget = gx_main.get_widget("treeview_similart_artists")
        BaseListController.__init__(self, widget)
    
    def on_duble_click(self):
        artist = self.get_selected_item()
        LOG.debug("Clicked Similar Artist:", artist)
        self.search_panel.set_text(artist)
        
class SimilartTagsController(BaseListController):
    def __init__(self, gx_main, search_panel):
        self.search_panel = search_panel
        widget = gx_main.get_widget("treeview_song_tags")
        BaseListController.__init__(self, widget)
    
    def on_duble_click(self):
        tags = self.get_selected_item()
        LOG.debug("Clicked tags:", tags)
        self.search_panel.set_text(tags)        
        
                
        
API_KEY = FConfiguration().API_KEY
API_SECRET = FConfiguration().API_SECRET

username = FConfiguration().lfm_login
password_hash = pylast.md5(FConfiguration().lfm_password)
#TODO: This file is under heavy refactoring, don't touch anything you think is wrong

try:
    lastfm = pylast.get_lastfm_network(api_key=API_KEY, api_secret=API_SECRET, username=username, password_hash=password_hash)
except:
    lastfm = None
    LOG.error("last.fm connection error")


class InformationController():
    def __init__(self,gx_main, playerCntr, directoryCntr, search_panel):
        
        self.album_image = gx_main.get_widget("image_widget")
        
        """album name"""
        self.album_name = gx_main.get_widget("label_album_name")        
        self.album_name.set_use_markup(True)
        
        self.current_song_label = gx_main.get_widget("current_song_label")
        self.current_song_label.set_use_markup(True)
        
        """Similar artists"""
        self.similar_artists_cntr = SimilartArtistsController(gx_main, search_panel)
        self.similar_artists_cntr.set_title(_('Song Artists'))     
        
        """similar songs"""
        self.similar_songs_cntr = SimilartSongsController(gx_main, playerCntr, directoryCntr)              
        self.similar_songs_cntr.set_title(_("Similar Songs"))   
        
        """song tags"""       
        self.song_tags_cntr = SimilartTagsController(gx_main,search_panel)
        self.song_tags_cntr.set_title(_("Similar Tags"))
        
        """link buttons"""
        self.lastfm_url = gx_main.get_widget("lastfm_linkbutton")
        self.wiki_linkbutton = gx_main.get_widget("wiki_linkbutton")
        self.mb_linkbutton = gx_main.get_widget("mb_linkbutton")
        
        
        
        self.last_album_name = None
        
        self.last_fm_network = lastfm
    
    def show_song_info(self, song):
        thread.start_new_thread(self.show_song_info_tread, (song,))
        #self.show_song_info_tread(song)
    
    def add_similar_song(self, song):
        self.current_list_model.append([song.get_short_description(), song.path])
        #self.similar_songs_cntr.add_item(song.get_name())
    
    def add_similar_artist(self, artist):
        self.similar_artists_cntr.add_item(artist)
    
    def add_tag(self, tag):
        self.song_tags_cntr.add_item(tag)
    
    def show_song_info_tread(self, song):
        self.song = song
        LOG.info("Get all possible information about song")
        image_url = self.get_album_image_url(song)        
        if not image_url:
            LOG.info("Image not found, load empty.")
            self.album_image.set_from_file("share/pixmaps/blank-disk.jpg")
            return None
    
        image_pix_buf = self.create_pbuf_image_from_url(image_url)
        self.album_image.set_from_pixbuf(image_pix_buf)
        
    def set_image(self, path):
        pass
    
    def get_album_image_url(self, song):
        
        """set urls"""
        self.lastfm_url.set_uri("http://www.lastfm.ru/search?q="+song.getArtist()+"&type=artist")
        self.wiki_linkbutton.set_uri("http://en.wikipedia.org/w/index.php?search="+song.getArtist())
        self.mb_linkbutton.set_uri("http://musicbrainz.org/search/textsearch.html?type=artist&query="+song.getArtist())

        
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
        self.song_tags_cntr.clear()
        for tag in tags:
            try:            
                tag_item = tag.item
            except AttributeError:
                tag_item = tag['item']
            self.add_tag(tag_item.get_name())
        
        """similar artists"""
        artist = track.get_artist()
        similar_artists = artist.get_similar(30)
       
        self.similar_artists_cntr.clear()
        for artist in similar_artists:
            try:            
                artist_item = artist.item
            except AttributeError:
                artist_item = artist['item']
            self.add_similar_artist(artist_item.get_name())
        
        album = track.get_album()
        if album:           
            self.album_name.set_markup("<b>" +song.getArtist() + " - " +  album.get_name()+" ("+album.get_release_year()+")</b>")
        
                
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
 
        
