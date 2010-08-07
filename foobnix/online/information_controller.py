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
        try:
            pix = gtk.gdk.pixbuf_new_from_file("/usr/local/share/pixmaps/blank-disc.jpg") #@UndefinedVariable
            self.album_image.set_from_pixbuf(pix)
        except:
            try:
                pix = gtk.gdk.pixbuf_new_from_file("/usr/share/pixmaps/blank-disc.jpg") #@UndefinedVariable
                self.album_image.set_from_pixbuf(pix)
            except:    
                pix = gtk.gdk.pixbuf_new_from_file("foobnix/pixmaps/blank-disc.jpg") #@UndefinedVariable
                self.album_image.set_from_pixbuf(pix)

    def __init__(self, gx_main, playerCntr, directoryCntr, search_panel):
        
        self.album_image = gx_main.get_widget("image_widget")
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
        thread.start_new_thread(self.show_song_info_tread, (song,))
        #    self.show_song_info_tread(song)
    
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
        
        #    LOG.error("Image url dowlaod error")
        #    image_url = None
            
        if not image_url:
            LOG.info("Image not found, load empty.")
            self.set_no_image_album()
            return None
    
        try:
            image_pix_buf = self.create_pbuf_image_from_url(image_url)
            self.album_image.set_from_pixbuf(image_pix_buf)
        except:
            LOG.error("dowload image error")
        
        
    def set_image(self, path):
        pass
    
    def get_album_image_url(self, song):
        
        """set urls"""
        """TODO TypeError: cannot concatenate 'str' and 'NoneType' objects """
        self.lastfm_url.set_uri("http://www.lastfm.ru/search?q=" + song.getArtist() + "&type=artist")
        self.wiki_linkbutton.set_uri("http://en.wikipedia.org/w/index.php?search=" + song.getArtist())
        self.mb_linkbutton.set_uri("http://musicbrainz.org/search/textsearch.html?type=artist&query=" + song.getArtist())

        
        self.current_song_label.set_markup("<b>" + song.getTitle() + "</b>")
        
        
        track = self.last_fm_network.get_track(song.getArtist(), song.getTitle())
        
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
        
        album = track.get_album()
        if album:           
            self.album_name.set_markup("<b>" + song.getArtist() + " - " + album.get_name() + " (" + album.get_release_year() + ")</b>")
        else:
            self.album_name.set_markup(u"<b>" + song.getArtist() + "</b>")
                
            
                
        #album = self.last_fm_network.get_album(song.getArtist(), song.getTitle())
        
        
        if not album:
            return None
        
        
       
        
        LOG.info("Find album", album)
        
        
        if self.last_album_name == album.get_name():
            LOG.info("Album the same, not need to dowlaod image")
            #TODO  need to implement album image cache
            return self.last_image
        
        if not album:
            return None
        
        LOG.info(album)
        try:
            self.last_album_name = album.get_name()            
            self.last_image = album.get_cover_image(size=pylast.COVER_EXTRA_LARGE)
        except:            
            LOG.info("image not found for:", song)
        
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
 
        
