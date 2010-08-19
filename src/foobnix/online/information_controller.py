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
from foobnix.online.song_resource import update_song_path
from foobnix.util.mouse_utils import  is_double_left_click, \
    is_rigth_click
from foobnix.online.dowload_util import save_song_thread, save_as_song_thread
from foobnix.lyric.lyr import get_lyrics
import os

class SimilartSongsController(BaseListController):
    
        def __init__(self, gx_main, playerCntr, directoryCntr):
            self.directoryCntr = directoryCntr
            self.playerCntr = playerCntr
            widget = gx_main.get_widget("treeview_similar_songs")
            widget.get_parent().set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
            BaseListController.__init__(self, widget)
            
            self.parent = "Similar to"
            
        def on_drag(self):
            items = self.get_all_items()
            songs = []
            similar = _("Similar to: ") + self.parent
            song = CommonBean(name=similar, type=CommonBean.TYPE_FOLDER)
            songs.append(song)
            for item in items:                
                song = CommonBean(name=item, type=CommonBean.TYPE_MUSIC_URL, parent=similar)
                songs.append(song)
            self.directoryCntr.append_virtual(songs)
        
        def play_selected_song(self):
            artist_track = self.get_selected_item()
            song = CommonBean(name=artist_track, type=CommonBean.TYPE_MUSIC_URL)
            update_song_path(song)
            self.playerCntr.playSong(song)
        
        def show_save_as_dialog(self, song):
            LOG.debug("Show Save As Song dialog")    
            chooser = gtk.FileChooserDialog(title=_("Choose directory to save song"), action=gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, buttons=(gtk.STOCK_OPEN, gtk.RESPONSE_OK))
            chooser.set_default_response(gtk.RESPONSE_OK)
            response = chooser.run()
            if response == gtk.RESPONSE_OK:
                path = chooser.get_filename()
                save_as_song_thread(song, path)
            elif response == gtk.RESPONSE_CANCEL:
                LOG.info('Closed, no files selected')
            chooser.destroy()
            
        def show_info(self, song):
            md = gtk.MessageDialog(None, gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO,
                                   gtk.BUTTONS_CLOSE, song.getArtist() + " - " + song.getTitle())
            md.run()
            md.destroy()
            
            
        def on_button_press(self, w, e):
            if is_double_left_click(e):
                self.play_selected_song()
                    
            if is_rigth_click(e):
                artist_track = self.get_selected_item()
                song = CommonBean(name=artist_track, type=CommonBean.TYPE_MUSIC_URL)

                
                menu = gtk.Menu()
                
                play = gtk.ImageMenuItem(gtk.STOCK_MEDIA_PLAY)
                play.connect("activate", lambda * a: self.play_selected_song())
                menu.add(play)
                
                save = gtk.ImageMenuItem(gtk.STOCK_SAVE)
                save.connect("activate", lambda * a: save_song_thread([song]))            
                menu.add(save)
                
                save_as = gtk.ImageMenuItem(gtk.STOCK_SAVE_AS)
                save_as.connect("activate", lambda * a: self.show_save_as_dialog([song]))
                menu.add(save_as)
                
                add = gtk.ImageMenuItem(gtk.STOCK_ADD)
                add.connect("activate", lambda * a: self.on_drag())
                menu.add(add)
    
                remove = gtk.ImageMenuItem(gtk.STOCK_REMOVE)
                remove.connect("activate", lambda * a: self.remove_selected())
                menu.add(remove)
                
                info = gtk.ImageMenuItem(gtk.STOCK_INFO)
                info.connect("activate", lambda * a: self.show_info(song))
                menu.add(info)
                
                menu.show_all()
                menu.popup(None, None, None, e.button, e.time)    

class SimilartArtistsController(BaseListController):
    def __init__(self, gx_main, search_panel):
        self.search_panel = search_panel
        widget = gx_main.get_widget("treeview_similart_artists")
        widget.get_parent().set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        BaseListController.__init__(self, widget)
    
    def on_button_press(self, w, e):
        if is_double_left_click(e):
            artist = self.get_selected_item()
            LOG.debug("Clicked Similar Artist:", artist)
            self.search_panel.set_text(artist)
        
class SimilartTagsController(BaseListController):
    def __init__(self, gx_main, search_panel):
        self.search_panel = search_panel
        widget = gx_main.get_widget("treeview_song_tags")
        widget.get_parent().set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        BaseListController.__init__(self, widget)
    
    def on_button_press(self, w, e):
        if is_double_left_click(e):
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
    

    def set_no_image_album(self):
        
        heigth = gtk.gdk.screen_height()            
        if heigth < 800:
            image_name = "blank-disc-small.jpg"
        else:
            image_name = "blank-disc.jpg"
        
        try:
            pix = gtk.gdk.pixbuf_new_from_file("/usr/local/share/pixmaps/" + image_name) #@UndefinedVariable
        except:
            try:
                pix = gtk.gdk.pixbuf_new_from_file("/usr/share/pixmaps/" + image_name) #@UndefinedVariable
            except:    
                pix = gtk.gdk.pixbuf_new_from_file("foobnix/pixmaps/" + image_name) #@UndefinedVariable
        
        self.album_image.set_from_pixbuf(pix)
        self.lyric_image_widget.set_from_pixbuf(pix)
        self.info_thread = None
             

    def __init__(self, gx_main, playerCntr, directoryCntr, search_panel):
        
        self.album_image = gx_main.get_widget("image_widget")
        self.lyric_image_widget = gx_main.get_widget("lyric_image_widget")
        self.lyrics_text_widget = gx_main.get_widget("lyric_text")
        
        self.lyric_artist_title = gx_main.get_widget("lyric_artist_title")
        
        self.lyrics_buffer = self.lyrics_text_widget.get_buffer()
        self.set_no_image_album()
            
        
        """album name"""
        self.album_name = gx_main.get_widget("label_album_name")        
        self.album_name.set_use_markup(True)
        
        self.current_song_label = gx_main.get_widget("current_song_label")
        self.current_song_label.set_use_markup(True)
        
        """Similar artists"""
        self.similar_artists_cntr = SimilartArtistsController(gx_main, search_panel)
        self.similar_artists_cntr.set_title(_('Similar Artists'))     
        
        """similar songs"""
        self.similar_songs_cntr = SimilartSongsController(gx_main, playerCntr, directoryCntr)              
        self.similar_songs_cntr.set_title(_("Similar Songs"))   
        
        """song tags"""       
        self.song_tags_cntr = SimilartTagsController(gx_main, search_panel)
        self.song_tags_cntr.set_title(_("Similar Tags"))
        
        """link buttons"""
        self.lastfm_url = gx_main.get_widget("lastfm_linkbutton")
        self.wiki_linkbutton = gx_main.get_widget("wiki_linkbutton")
        self.mb_linkbutton = gx_main.get_widget("mb_linkbutton")
        
        
        
        self.last_album_name = None
        self.last_image = None
        
        self.last_fm_network = lastfm
    
    def show_song_info(self, song):
        if (FConfiguration().view_info_panel or FConfiguration().view_lyric_panel) and not self.info_thread:
            self.info_thread = thread.start_new_thread(self.show_song_info_tread, (song,))
            #self.show_song_info_tread(song)
        else:
            LOG.warn("Please try later... search is not finished")
            
    
    def add_similar_song(self, song):
        self.current_list_model.append([song.get_short_description(), song.path])
        #self.similar_songs_cntr.add_item(song.get_name())
    
    def add_similar_artist(self, artist):
        self.similar_artists_cntr.add_item(artist)
    
    def add_tag(self, tag):
        self.song_tags_cntr.add_item(tag)
    
    def show_song_info_tread(self, song):        
        self.song = song
        
        if not song.getArtist() or not song.getTitle():
            LOG.warn("For update info artist and title are required", song.name, song.getArtist(), song.getTitle())
            self.info_thread = None
            return None
        
        LOG.info("Update song info", song.name, song.getArtist(), song.getTitle())
        try:
            track = self.last_fm_network.get_track(song.getArtist(), song.getTitle())
            album = track.get_album()
        except:
            LOG.error("Error getting track and album from last.fm")
            self.set_no_image_album()
            self.info_thread = None
            return None
        
        if song.image:
            self.update_image_from_file(song)
        else:
            self.update_image_from_url(album)
        
        self.update_lyrics(song)
        self.update_links(song)
        self.update_info_panel(song, track, album)
        
        
        self.info_thread = None
    
    def update_image_from_file(self, song):
        if os.path.isfile(song.image):
            pixbuf = gtk.gdk.pixbuf_new_from_file(song.image)            #@UndefinedVariable
            heigth = gtk.gdk.screen_height() #@UndefinedVariable
            
            if heigth < 800:
                LOG.info("Image size 174x174")
                scaled_buf = pixbuf.scale_simple(174, 174, gtk.gdk.INTERP_BILINEAR) #@UndefinedVariable
            else:
                LOG.info("Image size 300x300")
                scaled_buf = pixbuf.scale_simple(300, 300, gtk.gdk.INTERP_BILINEAR) #@UndefinedVariable
            
            self.album_image.set_from_pixbuf(scaled_buf)
            self.lyric_image_widget.set_from_pixbuf(scaled_buf)
        else:
            LOG.error("Song image not found", song)
    
    def update_image_from_url(self, album):        
            
        image_url = self.get_album_image_url(album)            
     
        if not image_url:
            LOG.info("Image not found, load empty.")
            self.set_no_image_album()
            self.info_thread = None
            return None
    
        try:
            image_pix_buf = self.create_pbuf_image_from_url(image_url)
            heigth = gtk.gdk.screen_height() #@UndefinedVariable
            if heigth < 800:
                LOG.info("Image size 174x174")
                image_pix_buf = image_pix_buf.scale_simple(174, 174, gtk.gdk.INTERP_BILINEAR) #@UndefinedVariable
            else:
                LOG.info("Image size 300x300")
                image_pix_buf = image_pix_buf.scale_simple(300, 300, gtk.gdk.INTERP_BILINEAR) #@UndefinedVariable
            
            
            self.album_image.set_from_pixbuf(image_pix_buf)
            self.lyric_image_widget.set_from_pixbuf(image_pix_buf)
        except:
            LOG.error("dowload image error")
            self.set_no_image_album()
        
    def update_lyrics(self, song):
        if song.getArtist() and song.getTitle():
            try:
                lyric = get_lyrics(song.getArtist(), song.getTitle())
            except:
                lyric = None
                LOG.error("Lyrics get error")
                pass
            if lyric:
                self.lyrics_buffer.set_text(lyric)
            else:
                self.lyrics_buffer.set_text(_("Lyric not found"))
                
            self.lyric_artist_title.set_markup("<b>" + song.getArtist() + " - " + song.getTitle() + "</b>")
               
            self.current_song_label.set_markup("<b>" + song.getTitle() + "</b>")

    def update_links(self, song):
        """set urls"""
        """TODO TypeError: cannot concatenate 'str' and 'NoneType' objects """
        self.lastfm_url.set_uri("http://www.lastfm.ru/search?q=" + song.getArtist() + "&type=artist")
        self.wiki_linkbutton.set_uri("http://en.wikipedia.org/w/index.php?search=" + song.getArtist())
        self.mb_linkbutton.set_uri("http://musicbrainz.org/search/textsearch.html?type=artist&query=" + song.getArtist())
    
    def update_info_panel(self, song, track, album):
        self.similar_songs_cntr.parent = song.getArtist() + " - " + song.getTitle()
        
        LOG.info(track)
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
        tags = track.get_top_tags(15)        
        self.song_tags_cntr.clear()
        for tag in tags:
            try:            
                tag_item = tag.item
            except AttributeError:
                tag_item = tag['item']
            self.add_tag(tag_item.get_name())
        
        """similar artists"""
        artist = track.get_artist()
        similar_artists = artist.get_similar(15)
       
        self.similar_artists_cntr.clear()
        for artist in similar_artists:
            try:            
                artist_item = artist.item
            except AttributeError:
                artist_item = artist['item']
            self.add_similar_artist(artist_item.get_name())
        
        if album:           
            self.album_name.set_markup("<b>" + song.getArtist() + " - " + album.get_name() + " (" + album.get_release_year() + ")</b>")
        else:
            self.album_name.set_markup(u"<b>" + song.getArtist() + "</b>")
                
    
    def get_album_image_url(self, album):
        if not album:
            return None
        
        if self.last_album_name == album.get_name():
            LOG.info("Album the same, not need to dowlaod image")
            #TODO  need to implement album image cache
            return self.last_image
        
       
        LOG.info(album)
        try:
            self.last_album_name = album.get_name()
            
            heigth = gtk.gdk.screen_height()                
            if heigth < 800:
                self.last_image = album.get_cover_image(size=pylast.COVER_LARGE)                       
            else:
                self.last_image = album.get_cover_image(size=pylast.COVER_EXTRA_LARGE)            
                
        except:            
            LOG.info("image not found for:")
        
        LOG.info("image:", self.last_image)        
        return self.last_image
    
    def create_pbuf_image_from_url(self, url_to_image):
        f = urllib.urlopen(url_to_image)
        data = f.read()
        pbl = gtk.gdk.PixbufLoader() #@UndefinedVariable
        pbl.write(data)
        pbuf = pbl.get_pixbuf()
        pbl.close()
        return pbuf   
 
        
