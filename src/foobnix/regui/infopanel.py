'''
Created on Sep 23, 2010

@author: ivan
'''
import os
import gtk
import copy
import gobject
import logging

from foobnix.fc.fc import FC
from foobnix.regui.model import FModel
from foobnix.regui.state import LoadSave
from foobnix.helpers.image import ImageBase
from foobnix.helpers.textarea import TextArea
from foobnix.regui.model.signal import FControl
from foobnix.helpers.my_widgets import EventLabel
from foobnix.helpers.pref_widgets import HBoxDecoratorTrue
from foobnix.fc.fc_cache import FCache, COVERS_DIR, LYRICS_DIR 
from foobnix.regui.treeview.simple_tree import SimpleTreeControl
from foobnix.util.const import FTYPE_NOT_UPDATE_INFO_PANEL, \
    LEFT_PERSPECTIVE_INFO, ICON_BLANK_DISK, SITE_LOCALE
from foobnix.util.bean_utils import update_parent_for_beans, \
    update_bean_from_normalized_text
from foobnix.thirdparty.lyr import get_lyrics
from foobnix.regui.service.lyrics_parsing_service import get_lyrics_by_parsing


class InfoCache():
    def __init__(self):
        self.best_songs_bean = None
        self.similar_tracks_bean = None
        self.similar_artists_bean = None
        self.similar_tags_bean = None
        self.lyric_bean = None
        self.wiki_artist = None
        
        self.active_method = None

class InfoPanelWidget(gtk.Frame, LoadSave, FControl):   
    def __init__(self, controls): 
        gtk.Frame.__init__(self)
        FControl.__init__(self, controls)
        
        self.album_label = gtk.Label()
        self.album_label.set_line_wrap(True)
        self.album_label.set_markup("<b></b>")
        self.set_label_widget(self.album_label)                                
        
        self.empty = TextArea()
        
        self.best_songs = SimpleTreeControl(_("Best Songs"), controls)
        self.best_songs.line_title = EventLabel(self.best_songs.get_title(), func=self.show_current, arg=self.best_songs, func1=self.show_best_songs)
        
        self.artists = SimpleTreeControl(_("Similar Artists"), controls)
        self.artists.line_title = EventLabel(self.artists.get_title(), func=self.show_current, arg=self.artists, func1=self.show_similar_artists)
        
        self.tracks = SimpleTreeControl(_("Similar Songs"), controls)
        self.tracks.line_title = EventLabel(self.tracks.get_title(), func=self.show_current, arg=self.tracks, func1=self.show_similar_tracks)
                
        self.tags = SimpleTreeControl(_("Similar Tags"), controls)
        self.tags.line_title = EventLabel(self.tags.get_title(), func=self.show_current, arg=self.tags, func1=self.show_similar_tags)
        
        
        self.lyrics = TextArea()
        lyric_title = _("Lyrics")
        self.lyrics.set_text("", lyric_title)
        self.lyrics.line_title = EventLabel(lyric_title, func=self.show_current, arg=self.lyrics, func1=self.show_similar_lyrics)
        
        
        """wiki"""
        wBox = gtk.VBox()
        wiki_title = _("About Artist")
        self.wiki = TextArea()
        
        wBox.line_title = EventLabel(wiki_title, func=self.show_current, arg=wBox, func1=self.show_wiki_info)
        
        """info"""
        info_frame = gtk.Frame(_("Info"))
        
        self.last_fm_label = gtk.LinkButton("http://www.last.fm", "Last.Fm")
        self.wiki_label = gtk.LinkButton("http://www.wikipedia.org", "Wikipedia")
        
        info_line = HBoxDecoratorTrue(self.last_fm_label, self.wiki_label)
        info_frame.add(info_line)
        
        """downloads"""
        dm_frame = gtk.Frame(_("Downloads"))
                
        self.exua_label = gtk.LinkButton("http://www.ex.ua", "EX.ua")
        self.rutracker_label = gtk.LinkButton("http://rutracker.org", "Rutracker")
        
        dm_line = HBoxDecoratorTrue(self.exua_label, self.rutracker_label)
        dm_frame.add(dm_line)
        
        
        self.wiki = TextArea()
        self.wiki.set_text("", wiki_title)
        
        wBox.pack_start(HBoxDecoratorTrue(info_frame, dm_frame), False, False)
        wBox.pack_start(self.wiki, True, True)
        
        wBox.scroll = wBox
        
        self.vpaned_small = gtk.VBox(False, 0)
        
        """image and similar artists"""
        ibox = gtk.HBox(False, 0)
        self.image = ImageBase(ICON_BLANK_DISK, FC().info_panel_image_size)
        
        
        lbox = gtk.VBox(False, 0)
        
        
        self.left_widget = [wBox, self.artists, self.tracks, self.tags, self.lyrics, self.best_songs]
        
        for l_widget in self.left_widget:        
            lbox.pack_start(l_widget.line_title)
                
        ibox.pack_start(self.image, False, False)
        ibox.pack_start(lbox, True, True)
                
        """image and similar artists"""
        sbox = gtk.VBox(False, 0)
        
        for l_widget in self.left_widget:        
            sbox.pack_start(l_widget.scroll, True, True)
        
        sbox.pack_end(self.empty.scroll, True, True)
        
        self.vpaned_small.pack_start(ibox, False, False)
        self.vpaned_small.pack_start(sbox, True, True)
                
        self.add(self.vpaned_small)
        
        self.hide_all()
        
        self.bean = None
        self.info_cache = InfoCache()
    
    def activate_perspective(self):
        FC().left_perspective = LEFT_PERSPECTIVE_INFO
    
    def show_current(self, widget):
        if not self.controls.net_wrapper.is_internet():
            return;
        
        def safe_task():
            self.empty.hide()
            if widget.line_title.selected:
                widget.scroll.hide()
                self.empty.show()
                widget.line_title.set_not_active()
                self.info_cache.active_method
                return
        
            for w in self.left_widget:
                w.scroll.hide()
                w.line_title.set_not_active()
        
            widget.scroll.show_all()
            widget.line_title.set_active()
        
            self.info_cache.active_method = widget.line_title.func1
            self.controls.in_thread.run_with_progressbar(widget.line_title.func1)
        gobject.idle_add(safe_task)
            
    def clear(self):
        self.image.set_no_image()
        self.tracks.clear_tree()
        self.tags.clear_tree()
        self.artists.clear_tree()
        
    def update_info_panel(self):
        if not self.controls.net_wrapper.is_internet():
            return;
        if not self.bean:
            return None
        bean = copy.copy(self.bean)
        
        def update_info_panel_task():
            self.show_disc_cover(bean)
            self.show_album_title(bean)
            if self.controls.coverlyrics.get_property("visible"):
                try:
                    self.show_similar_lyrics(bean)
                except Exception, e:
                    logging.error("Can't get lyrics. " + type(e).__name__ + ": " + e.message) 
            if self.info_cache.active_method:
                self.info_cache.active_method()
    
        self.controls.in_thread.run_with_progressbar(update_info_panel_task)
        
    def update(self, bean):
        if not self.controls.net_wrapper.is_internet():
            return;
                
        if bean.type == FTYPE_NOT_UPDATE_INFO_PANEL:
            return False
        
        self.clear()
        
        if not FC().is_view_info_panel:
            logging.debug("Info panel disabled")  
            return
        
        """check connection"""
        if not self.controls.lastfm_service.connect():
            return
       
        """update bean info form text if possible"""
        bean = update_bean_from_normalized_text(bean)
        
        if not bean.artist or not bean.title:
            logging.debug("Artist and title not defined")
        
        self.bean = bean
        
        self.update_info_panel()
        
    
    def show_album_title(self, bean=None):
        if not bean:
            bean = self.bean
        if bean.UUID != self.bean.UUID:
            return
        
        """update info album and year"""
        info_line = bean.artist
        if FCache().album_titles.has_key(bean.text):
            info_line = FCache().album_titles[bean.text]
        else:
            album_name = self.controls.lastfm_service.get_album_name(bean.artist, bean.title)
            album_year = self.controls.lastfm_service.get_album_year(bean.artist, bean.title)
            if album_name:
                info_line = album_name
            if album_name and album_year:
                info_line = album_name + "(" + album_year + ")"
            
            if isinstance(info_line, unicode) or isinstance(info_line, str) :
                FCache().album_titles[bean.text] = info_line
        if info_line and bean.UUID == self.bean.UUID:
            info_line = info_line.replace('&', '&amp;')
            self.album_label.set_markup("<b>%s</b>" % info_line)
            self.controls.coverlyrics.album_title.set_markup("<b>%s</b>" % info_line)
        
    def show_disc_cover(self, bean=None):
        if not bean:
            bean = self.bean
        if bean.UUID != self.bean.UUID:
            return
        dict = FCache().covers

        """update image"""
        if not bean.image:
            if not os.path.isdir(COVERS_DIR):
                os.mkdir(COVERS_DIR)
            list_images = os.listdir(COVERS_DIR)
            '''remove extra keys'''
            for key in dict.keys():
                if (key+'.jpg') not in list_images:
                    del dict[key]
            '''remove extra files'''
            for file in list_images:
                if (os.path.splitext(file)[0] not in dict.keys() 
                   and os.path.isfile(os.path.join(COVERS_DIR, file))):
                    os.remove(os.path.join(COVERS_DIR, file))
            
            for list, key in zip(dict.values(), dict.keys()):
                if bean.text in list:
                    bean.image = os.path.join(COVERS_DIR, key + ".jpg")
                    break
            
            if not bean.image:
                '''get image url'''
                bean.image = self.controls.lastfm_service.get_album_image_url(bean.artist, bean.title)       
        
        if not bean.image:
            logging.warning("""""Can't get cover image. Check the correctness of the artist's name and track title""""")
            
        '''make .jpg image and store it in cache'''        
        if bean.image and bean.image.startswith("http://"):
            url_basename = os.path.splitext(os.path.basename(bean.image))[0]
            if dict.has_key(url_basename):
                dict[url_basename].append(bean.text)
            else:
                dict[url_basename] = [bean.text]
                self.image.get_pixbuf().save(os.path.join(COVERS_DIR, url_basename + '.jpg'), "jpeg", {"quality":"90"})
        
        if bean.UUID == self.bean.UUID:
            self.image.update_info_from(bean)
            self.controls.trayicon.update_info_from(bean)
            self.controls.coverlyrics.set_cover()
        
        
    def show_similar_lyrics(self, bean=None):
        if not bean:
            bean = self.bean
        if bean.UUID != self.bean.UUID:
            return
        if self.info_cache.lyric_bean == bean:
            return None
        
        self.info_cache.lyric_bean = bean
        
        """lyrics"""
        if not os.path.isdir(LYRICS_DIR):
            os.mkdir(LYRICS_DIR)
        lyrics_list = os.listdir(LYRICS_DIR)
        lyrics_title = "%s - %s" % (bean.artist, bean.title)
        text = None

        if lyrics_title.lower().strip() in lyrics_list:
            text = "".join(open(os.path.join(LYRICS_DIR, lyrics_title.lower().strip()), 'r').readlines())
        else:
            try:
                logging.debug("Try to get lyrics from lyrics.wikia.com")
                text = get_lyrics(bean.artist, bean.title)
            except:
                logging.info("Error occurred when getting lyrics from lyrics.wikia.com")
            if not text:
                text = get_lyrics_by_parsing(bean.artist, bean.title)
            if text:
                open(os.path.join(LYRICS_DIR, lyrics_title.lower().strip()), 'w').write(text)
            else:
                logging.info("The text not found")
                text = "The text not found"
        if bean.UUID == self.bean.UUID:
            self.lyrics.set_text(text, lyrics_title)
            self.controls.coverlyrics.lyrics.set_text(text, lyrics_title)
        
    def show_wiki_info(self):
        if not self.bean:
            return
        if self.info_cache.wiki_artist == self.bean.artist:
            return None
        self.info_cache.wiki_artist = self.bean.artist    
        
        
        self.wiki_label.set_uri("http://%s.wikipedia.org/w/index.php?&search=%s" %(SITE_LOCALE, self.bean.artist))
        self.last_fm_label.set_uri("http://www.last.fm/search?q=%s" % self.bean.artist)
        
        self.exua_label.set_uri("http://www.ex.ua/search?s=%s" % self.bean.artist)
        self.rutracker_label.set_uri("http://rutracker.org/forum/tracker.php?nm=%s" % self.bean.artist)
        
        artist = self.controls.lastfm_service.get_network().get_artist(self.bean.artist)        
        self.wiki.set_text(artist.get_bio_content(), self.bean.artist)
        
        images = artist.get_images(limit=6)
        
        for image in images:
            try:
                url = image.sizes.large
            except AttributeError:
                url = image.sizes["large"]
            self.wiki.append_image(url)

    def show_similar_tags(self):
        if self.info_cache.similar_tags_bean == self.bean:
            return None
        self.info_cache.similar_tags_bean = self.bean
        
        """similar  tags"""
        similar_tags = self.controls.lastfm_service.search_top_similar_tags(self.bean.artist, self.bean.title)
        parent = FModel("Similar Tags: " + self.bean.title)
        update_parent_for_beans(similar_tags, parent)
        self.tags.populate_all([parent] + similar_tags)
        
    def show_similar_tracks(self):
        if self.info_cache.similar_tracks_bean == self.bean:
            return None
        self.info_cache.similar_tracks_bean = self.bean
        
        """similar  songs"""
        similar_tracks = self.controls.lastfm_service.search_top_similar_tracks(self.bean.artist, self.bean.title)
        parent = FModel("Similar Tracks: " + self.bean.title)
        update_parent_for_beans(similar_tracks, parent)
        self.tracks.populate_all([parent] + similar_tracks)
    
    def show_similar_artists(self):
        if self.info_cache.similar_artists_bean == self.bean:
            return None
        self.info_cache.similar_artists_bean = self.bean
        
        """similar  artists"""
        similar_artists = self.controls.lastfm_service.search_top_similar_artist(self.bean.artist)
        parent = FModel("Similar Artists: " + self.bean.artist)
        update_parent_for_beans(similar_artists, parent)
        self.artists.populate_all([parent] + similar_artists)
    
    def show_best_songs(self):         
        if self.info_cache.best_songs_bean == self.bean:
            return None
        
        self.info_cache.best_songs_bean = self.bean
        
        best_songs = self.controls.lastfm_service.search_top_tracks(self.bean.artist)
        parent = FModel("Best Songs: " + self.bean.artist)
        update_parent_for_beans(best_songs, parent)
        self.best_songs.populate_all([parent] + best_songs)
        
    def on_load(self):
        for w in self.left_widget:
            w.scroll.hide()
            w.line_title.set_not_active()
        self.empty.show()
        FCache().on_load()

    def on_save(self):
        pass    
    
    def on_quit(self):
        FCache().on_quit()     
