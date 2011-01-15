'''
Created on Sep 23, 2010

@author: ivan
'''
import gtk
from foobnix.regui.state import LoadSave
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl
from foobnix.regui.model import FModel
from foobnix.regui.treeview.simple_tree import SimpleTreeControl
from foobnix.util.const import FTYPE_NOT_UPDATE_INFO_PANEL, \
    LEFT_PERSPECTIVE_INFO, ICON_BLANK_DISK
from foobnix.helpers.my_widgets import EventLabel
from foobnix.helpers.textarea import TextArea
from foobnix.thirdparty.lyr import get_lyrics
import gobject
from foobnix.helpers.image import ImageBase
from foobnix.util.bean_utils import update_parent_for_beans, \
    update_bean_from_normalized_text
from foobnix.util import LOG

class InfoCache():
    def __init__(self):
        self.best_songs_bean = None
        self.similar_tracks_bean = None
        self.similar_artists_bean = None
        self.similar_tags_bean = None
        self.lyric_bean = None
        
        self.active_method = None

class InfoPanelWidget(gtk.Frame, LoadSave, FControl):   
    def __init__(self, controls): 
        gtk.Frame.__init__(self)
        FControl.__init__(self, controls)
        self.album_label = gtk.Label()
        self.album_label.set_line_wrap(True)
        self.album_label.set_markup("<b></b>")
        self.set_label_widget(self.album_label)                                
        
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
        
        
        self.vpaned_small = gtk.VBox(False, 0)
        
        """image and similar artists"""
        ibox = gtk.HBox(False, 0)
        self.image = ImageBase(ICON_BLANK_DISK, FC().info_panel_image_size)
        
        
        lbox = gtk.VBox(False, 0)
        
        
        self.left_widget = [self.artists, self.tracks, self.tags, self.lyrics, self.best_songs]
        
        for l_widget in self.left_widget:        
            lbox.pack_start(l_widget.line_title)
        

        
        ibox.pack_start(self.image, False, False)
        ibox.pack_start(lbox, True, True)
        
        
        """image and similar artists"""
        sbox = gtk.VBox(False, 0)
        
        for l_widget in self.left_widget:        
            sbox.pack_start(l_widget.scroll, True, True)
        
        self.vpaned_small.pack_start(ibox, False, False)
        self.vpaned_small.pack_start(sbox, True, True)
                
        self.add(self.vpaned_small)
        
        self.hide_all()
        
        self.bean = None
        self.info_cache = InfoCache()
    
    def activate_perspective(self):
        FC().left_perspective = LEFT_PERSPECTIVE_INFO
    
    def show_current(self, widget):
        for w in self.left_widget:
            w.scroll.hide()
            w.line_title.set_not_active()
            
        widget.scroll.show_all()
        widget.line_title.set_active()
        
        self.info_cache.active_method = widget.line_title.func1
        self.controls.in_thread.run_with_progressbar(widget.line_title.func1)
        
    
    def clear(self):
        self.image.set_no_image()
        self.tracks.clear_tree()
        self.tags.clear_tree()
        self.artists.clear_tree()
        
    def update_info_panel(self):
        if not self.bean:
            return None
        def task():
            self.show_disc_cover()
            
            if FC().left_perspective == LEFT_PERSPECTIVE_INFO:
                self.show_album_title()
                self.info_cache.active_method()
    
        self.controls.in_thread.run_with_progressbar(task)
        
    def update(self, bean):        
        #self.bean = bean
        
        if bean.type == FTYPE_NOT_UPDATE_INFO_PANEL:
            return False
        
        self.clear()    
        
        if not FC().is_view_info_panel:
            LOG.debug("Info panel disabled")  
            return
        
        """check connection"""
        if not self.controls.lastfm.connect():
            return

        """update bean info form text if possible"""
        bean = update_bean_from_normalized_text(bean)
        
        if not bean.artist or not bean.title:
            LOG.debug("Artist and title not defined")
            #return None
        
        self.bean = bean
        
        self.update_info_panel()
        
    
    def show_album_title(self):
        bean = self.bean
        """update info album and year"""
        
        album_name = self.controls.lastfm.get_album_name(bean.artist, bean.title)
        album_year = self.controls.lastfm.get_album_year(bean.artist, bean.title)
        def task():
            info_line = bean.artist        
            if album_name:
                info_line = album_name
            if album_name and album_year:
                info_line = album_name + "(" + album_year + ")"
                
            self.album_label.set_markup("<b>%s</b>" % info_line)
        gobject.idle_add(task)
    
    def show_disc_cover(self):
        bean = self.bean
        
        """update image"""
        if not bean.image:
            bean.image = self.controls.lastfm.get_album_image_url(bean.artist, bean.title)
        
        self.image.update_info_from(bean)
        self.controls.trayicon.update_info_from(bean)
        
    def show_similar_lyrics(self):
        if self.info_cache.lyric_bean == self.bean:
            return None
        self.info_cache.lyric_bean = self.bean
        
        """lyrics"""
        text = get_lyrics(self.bean.artist, self.bean.title)
        lyrics_title = "*** %s - %s *** \n" % (self.bean.artist, self.bean.title)
        self.lyrics.set_text(text, lyrics_title)
    
    def show_similar_tags(self):
        if self.info_cache.similar_tags_bean == self.bean:
            return None
        self.info_cache.similar_tags_bean = self.bean
        
        """similar  tags"""
        similar_tags = self.controls.lastfm.search_top_similar_tags(self.bean.artist, self.bean.title)
        parent = FModel("Similar Tags: " + self.bean.title)
        update_parent_for_beans(similar_tags, parent)
        self.tags.populate_all([parent] + similar_tags)
    
    def show_similar_tracks(self):
        if self.info_cache.similar_tracks_bean == self.bean:
            return None
        self.info_cache.similar_tracks_bean = self.bean
        
        """similar  songs"""
        similar_tracks = self.controls.lastfm.search_top_similar_tracks(self.bean.artist, self.bean.title)
        parent = FModel("Similar Tracks: " + self.bean.title)
        update_parent_for_beans(similar_tracks, parent)
        self.tracks.populate_all([parent] + similar_tracks)
    
    def show_similar_artists(self):
        if self.info_cache.similar_artists_bean == self.bean:
            return None
        self.info_cache.similar_artists_bean = self.bean
        
        """similar  artists"""
        similar_artists = self.controls.lastfm.search_top_similar_artist(self.bean.artist)
        parent = FModel("Similar Artists: " + self.bean.artist)
        update_parent_for_beans(similar_artists, parent)
        self.artists.populate_all([parent] + similar_artists)
    
    def show_best_songs(self):         
        if self.info_cache.best_songs_bean == self.bean:
            return None
        
        self.info_cache.best_songs_bean = self.bean
        
        best_songs = self.controls.lastfm.search_top_tracks(self.bean.artist)
        parent = FModel("Best Songs: " + self.bean.artist)
        update_parent_for_beans(best_songs, parent)
        self.best_songs.populate_all([parent] + best_songs)
        
    def on_load(self):
        self.show_current(self.left_widget[0])
         
    def on_save(self):
        pass    
