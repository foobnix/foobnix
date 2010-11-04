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
from foobnix.util.const import FTYPE_NOT_UPDATE_INFO_PANEL
from foobnix.helpers.my_widgets import notetab_label
from foobnix.helpers.textarea import TextArea
from foobnix.thirdparty.lyr import get_lyrics
import gobject
from foobnix.helpers.image import ImageBase

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
        self.image = ImageBase("blank-disc-cut.jpg",FC().info_panel_image_size)
        
        self.artists = SimpleTreeControl("Similar Artist", controls).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)  
        
        ibox.pack_start(self.image, False, False)
        ibox.pack_start(self.artists.scroll, True, True)
        
        """image and similar artists"""
        sbox = gtk.VBox(False, 0)
        
        self.tracks = SimpleTreeControl("Similar Songs", controls).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)        
        self.tags = SimpleTreeControl("Similar Tags", controls).set_scrolled(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.lyrics = TextArea()
        
        self.left_widget = [self.tracks.scroll, self.tags.scroll, self.lyrics]
        
        sbox.pack_start(self.tracks.scroll, True, True)
        sbox.pack_start(self.lyrics, True, True)
        sbox.pack_start(self.tags.scroll, True, True)
        
        
        self.vpaned_small.pack1(ibox, False, False)
        
        lbox = gtk.HBox(False, 0)
        
        lbox.pack_start(notetab_label(func=self.show_current, arg=self.tracks.scroll, symbol="similars"))
        lbox.pack_start(notetab_label(func=self.show_current, arg=self.lyrics,symbol="lyric"))
        lbox.pack_start(notetab_label(func=self.show_current, arg=self.tags.scroll, symbol="tags"))
        
        sbox.pack_start(lbox,False,False)
        
        self.vpaned_small.pack2(sbox, True, True)
                
        self.add(self.vpaned_small)
        
        self.show_all()
    
    def show_current(self, widget):
        for w in self.left_widget:
            w.hide()
        widget.show_all()
        
    
    def clear(self):
        self.image.set_no_image()
        self.tracks.clear()
        self.tags.clear()
        self.artists.clear()
        self.almum_label.set_markup("")
        
    def update(self, bean):
        if bean.type == FTYPE_NOT_UPDATE_INFO_PANEL:
            return False
        
        self.clear()    
        
        if not FC().is_view_info_panel:
            print "Info panel disabled"  
            return      

        if not bean.artist or not bean.title:
            text_artist = bean.get_artist_from_text()
            text_title = bean.get_title_from_text()  
            if text_artist and text_title:
                bean.artist, bean.title = text_artist, text_title
        
        if not bean.artist or not bean.title:
            print """Artist and title no difined"""
            return None
                
        """update info"""
        album_name = self.controls.lastfm.get_album_name(bean.artist, bean.title)
        album_year = self.controls.lastfm.get_album_year(bean.artist, bean.title)
        
        info_line = bean.artist + " - " + bean.title
        if album_name:
            info_line = bean.artist + " - " + album_name + " - " + bean.title
        if album_name and album_year:
            info_line = bean.artist + " - " + album_name + "(" +album_year+ ")" +" - " + bean.title
        
        def task():
            self.almum_label.set_markup("<b>%s</b>" % info_line)
        gobject.idle_add(task)
        
        """update image"""
        if not bean.image:
            bean.image = self.controls.lastfm.get_album_image_url(bean.artist, bean.title)
        
        self.image.update_info_from(bean)
        self.controls.trayicon.update_info_from(bean)
        
        
        def update_parent(parent_bean, beans):    
            for bean in beans:
                bean.parent(parent_bean)
        
        """similar  artists"""
        similar_artists = self.controls.lastfm.search_top_similar_artist(bean.artist)
        parent = FModel("Similar Artists: " + bean.artist)
        update_parent(parent, similar_artists)
        self.artists.populate_all([parent] + similar_artists)
        
        """similar  songs"""
        similar_tracks = self.controls.lastfm.search_top_similar_tracks(bean.artist, bean.title)
        parent = FModel("Similar Tracks: " + bean.title)
        update_parent(parent, similar_tracks)
        self.tracks.populate_all([parent] + similar_tracks)
        
        """similar  tags"""
        similar_tags = self.controls.lastfm.search_top_similar_tags(bean.artist, bean.title)
        parent = FModel("Similar Tags: " + bean.title)
        update_parent(parent, similar_tags)
        self.tags.populate_all([parent] + similar_tags)       
        
        """lyrics"""
        text = get_lyrics(bean.artist, bean.title)
        self.lyrics.set_text(text)
     
    def on_load(self):
        self.vpaned_small.set_position(FC().vpaned_small)
        for i, w in enumerate(self.left_widget):
            if i >0:
                w.hide()
            
         
    def on_save(self):
        FC().vpaned_small = self.vpaned_small.get_position()    
