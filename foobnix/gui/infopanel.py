'''
Created on Sep 23, 2010

@author: ivan
'''
import os
import copy
import logging
import threading

from gi.repository import Gtk
from gi.repository import GLib

from foobnix.fc.fc import FC
from foobnix.gui.model import FModel
from foobnix.gui.state import LoadSave
from foobnix.helpers.image import ImageBase
from foobnix.helpers.textarea import TextArea
from foobnix.gui.model.signal import FControl
from foobnix.helpers.my_widgets import EventLabel
from foobnix.helpers.pref_widgets import HBoxDecoratorTrue, FrameDecorator
from foobnix.fc.fc_cache import FCache, COVERS_DIR, LYRICS_DIR
from foobnix.gui.treeview.simple_tree import SimpleTreeControl
from foobnix.util import idle_task
from foobnix.util.const import FTYPE_NOT_UPDATE_INFO_PANEL, \
    ICON_BLANK_DISK, SITE_LOCALE
from foobnix.util.bean_utils import update_parent_for_beans, \
    update_bean_from_normalized_text
from foobnix.thirdparty.lyr import get_lyrics
from foobnix.gui.service.lyrics_parsing_service import get_lyrics_by_parsing
from foobnix.util.id3_util import get_image_for_bean


class InfoCache():
    def __init__(self):
        self.best_songs_bean = None
        self.similar_tracks_bean = None
        self.similar_artists_bean = None
        self.similar_tags_bean = None
        self.lyric_bean = None
        self.wiki_artist = None

        self.active_method = None


class InfoPanelWidget(Gtk.Frame, LoadSave, FControl):
    def __init__(self, controls):
        Gtk.Frame.__init__(self)
        FControl.__init__(self, controls)

        self.album_label = Gtk.Label.new(None)
        self.album_label.set_line_wrap(True)
        self.album_label.set_markup("<b></b>")
        self.set_label_widget(self.album_label)

        self.empty = TextArea()

        self.best_songs = SimpleTreeControl(_("Best Songs"), controls)
        self.best_songs.line_title = EventLabel(self.best_songs.get_title(), func=self.show_current,
                                                arg=self.best_songs, func1=self.show_best_songs)

        self.artists = SimpleTreeControl(_("Similar Artists"), controls)
        self.artists.line_title = EventLabel(self.artists.get_title(), func=self.show_current,
                                             arg=self.artists, func1=self.show_similar_artists)

        self.tracks = SimpleTreeControl(_("Similar Songs"), controls)
        self.tracks.line_title = EventLabel(self.tracks.get_title(), func=self.show_current,
                                            arg=self.tracks, func1=self.show_similar_tracks)

        self.tags = SimpleTreeControl(_("Similar Tags"), controls)
        self.tags.line_title = EventLabel(self.tags.get_title(), func=self.show_current,
                                          arg=self.tags, func1=self.show_similar_tags)

        self.lyrics = TextArea()
        lyric_title = _("Lyrics")
        self.lyrics.set_text("", lyric_title)
        self.lyrics.line_title = EventLabel(lyric_title, func=self.show_current,
                                            arg=self.lyrics, func1=self.show_similar_lyrics)

        """wiki"""
        wBox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)
        wiki_title = _("About Artist")
        self.wiki = TextArea()

        wBox.line_title = EventLabel(wiki_title, func=self.show_current, arg=wBox, func1=self.show_wiki_info)

        """info"""
        self.last_fm_label = Gtk.LinkButton.new_with_label("http://www.last.fm", "Last.Fm")
        self.wiki_label = Gtk.LinkButton.new_with_label("http://www.wikipedia.org", "Wikipedia")
        info_line = HBoxDecoratorTrue(self.last_fm_label, self.wiki_label)
        info_frame = FrameDecorator(_("Info"), info_line, 0.5, 0.5)

        """downloads"""
        self.exua_label = Gtk.LinkButton.new_with_label("http://www.ex.ua", "EX.ua")
        self.rutracker_label = Gtk.LinkButton.new_with_label("http://rutracker.org", "Rutracker")
        dm_line = HBoxDecoratorTrue(self.exua_label, self.rutracker_label)
        dm_frame = FrameDecorator(_("Downloads"), dm_line, 0.5, 0.5)

        self.wiki = TextArea()
        self.wiki.set_text("", wiki_title)

        wBox.pack_start(HBoxDecoratorTrue(info_frame, dm_frame), False, False, 0)
        wBox.pack_start(self.wiki, True, True, 0)

        wBox.scroll = wBox

        self.vpaned_small = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        """image and similar artists"""
        ibox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        self.image = ImageBase(ICON_BLANK_DISK, FC().info_panel_image_size)

        lbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        self.left_widget = [wBox, self.artists, self.tracks, self.tags, self.lyrics, self.best_songs]

        for l_widget in self.left_widget:
            lbox.pack_start(l_widget.line_title, True, True, 0)

        ibox.pack_start(self.image, False, False, 0)
        ibox.pack_start(lbox, True, True, 0)

        """image and similar artists"""
        sbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 0)

        for l_widget in self.left_widget:
            sbox.pack_start(l_widget.scroll, True, True, 0)

        sbox.pack_end(self.empty.scroll, True, True, 0)

        self.vpaned_small.pack_start(ibox, False, False, 0)
        self.vpaned_small.pack_start(sbox, True, True, 0)

        self.add(self.vpaned_small)

        self.bean = None
        self.info_cache = InfoCache()
        self.update_lock = threading.Lock()
        self.clear()

    @idle_task
    def show_current(self, widget):
        if not self.controls.net_wrapper.is_internet():
            return

        self.empty.hide()
        if widget.line_title.selected:
            widget.scroll.hide()
            self.empty.show()
            widget.line_title.set_not_active()
            return

        for w in self.left_widget:
            w.scroll.hide()
            w.line_title.set_not_active()

        widget.scroll.show_all()
        widget.line_title.set_active()

        self.info_cache.active_method = widget.line_title.func1
        self.controls.in_thread.run_with_spinner(widget.line_title.func1)

    def clear(self):
        self.image.set_no_image()
        self.tracks.clear_tree()
        self.tags.clear_tree()
        self.artists.clear_tree()
        self.lyrics.set_text("", _("Lyrics"))

    def update_info_panel(self):
        if not self.controls.net_wrapper.is_internet() or not self.bean:
            return

        bean = copy.copy(self.bean)

        def update_info_panel_task():
            self.update_lock.acquire()
            try:
                self.show_album_title(bean)
                self.show_disc_cover(bean)
                if self.controls.coverlyrics.get_property("visible"):
                    try:
                        self.show_similar_lyrics(bean)
                    except Exception, e:
                        logging.error("Can't get lyrics. " + type(e).__name__ + ": " + e.message)
                if self.info_cache.active_method:
                    self.info_cache.active_method()
            except:
                pass
            self.update_lock.release()

        threading.Thread(target=update_info_panel_task).start()

    def update(self, bean):
        if bean.type == FTYPE_NOT_UPDATE_INFO_PANEL:
            return False

        self.clear()

        if not self.controls.net_wrapper.is_internet():
            return

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
        if bean.text in FCache().album_titles:
            info_line = FCache().album_titles[bean.text]
        else:
            album_name = self.controls.lastfm_service.get_album_name(bean.artist, bean.title)
            album_year = self.controls.lastfm_service.get_album_year(bean.artist, bean.title)
            if album_name:
                info_line = album_name
            if album_name and album_year:
                info_line = album_name + " (" + album_year + ")"

            if isinstance(info_line, unicode) or isinstance(info_line, str):
                FCache().album_titles[bean.text] = info_line
        if info_line and bean.UUID == self.bean.UUID:
            info_line = info_line.replace('&', '&amp;')
            GLib.idle_add(self.album_label.set_markup, "<b>%s</b>" % info_line)
            GLib.idle_add(self.controls.coverlyrics.album_title.set_markup, "<b>%s</b>" % info_line)

    def show_disc_cover(self, bean=None):
        if not bean:
            bean = self.bean
        if bean.UUID != self.bean.UUID:
            return

        """update image"""
        if not bean.image:
            if not os.path.isdir(COVERS_DIR):
                os.mkdir(COVERS_DIR)
            bean.image = get_image_for_bean(bean, self.controls)

        if not bean.image:
            logging.warning("""""Can't get cover image. Check the correctness of the artist's name and track title""""")

        if bean.UUID == self.bean.UUID:
            self.image.update_info_from(bean)
            self.controls.trayicon.update_info_from(bean)
            self.controls.coverlyrics.set_cover()

    def show_similar_lyrics(self, bean=None):
        if not bean:
            bean = self.bean
        if not bean:
            return
        if bean.UUID != self.bean.UUID:
            return

        """lyrics"""
        if not os.path.isdir(LYRICS_DIR):
            os.mkdir(LYRICS_DIR)

        cache_name = lyrics_title = "%s - %s" % (bean.artist, bean.title)

        illegal_chars = ["/", "#", ";", ":", "%", "*", "&", "\\"]
        for char in illegal_chars:
            cache_name = cache_name.replace(char, "_")
        cache_name = cache_name.lower().strip()

        text = None

        if os.path.exists(os.path.join(LYRICS_DIR, cache_name)):
            with open(os.path.join(LYRICS_DIR, cache_name), 'r') as cache_file:
                text = "".join(cache_file.readlines())
        else:
            self.lyrics.set_text(_("Loading..."), lyrics_title)
            try:
                logging.debug("Try to get lyrics from lyrics.wikia.com")
                text = get_lyrics(bean.artist, bean.title)
            except:
                logging.info("Error occurred when getting lyrics from lyrics.wikia.com")
            if not text:
                text = get_lyrics_by_parsing(bean.artist, bean.title)
            if text:
                with open(os.path.join(LYRICS_DIR, cache_name), 'w') as cache_file:
                    cache_file.write(text)
            else:
                logging.info("The text not found")
                text = _("The text not found")
        if bean.UUID == self.bean.UUID:
            self.set_lyrics(text, lyrics_title)

    def show_wiki_info(self):
        if not self.bean:
            return
        if self.info_cache.wiki_artist == self.bean.artist:
            return None
        self.info_cache.wiki_artist = self.bean.artist

        self.wiki_label.set_uri("http://%s.wikipedia.org/w/index.php?&search=%s" % (SITE_LOCALE, self.bean.artist))
        self.last_fm_label.set_uri("http://www.last.fm/search?q=%s" % self.bean.artist)

        self.exua_label.set_uri("http://www.ex.ua/search?s=%s" % self.bean.artist)
        self.rutracker_label.set_uri("http://rutracker.org/forum/tracker.php?nm=%s" % self.bean.artist)

        artist = self.controls.lastfm_service.get_network().get_artist(self.bean.artist)
        self.wiki.set_text(artist.get_bio_summary(), self.bean.artist)

#         Deprecated
#         images = artist.get_images(limit=6)
#
#         for image in images:
#             try:
#                 url = image.sizes.large
#             except AttributeError:
#                 url = image.sizes["large"]
#             self.wiki.append_image(url)

    def show_similar_tags(self):
        if self.info_cache.similar_tags_bean == self.bean:
            return None
        self.info_cache.similar_tags_bean = self.bean

        """similar  tags"""
        similar_tags = self.controls.lastfm_service.search_top_similar_tags(self.bean.artist, self.bean.title)
        parent = FModel(_("Similar Tags:") + " " + self.bean.title)
        update_parent_for_beans(similar_tags, parent)
        self.tags.populate_all([parent] + similar_tags)

    def show_similar_tracks(self):
        if self.info_cache.similar_tracks_bean == self.bean:
            return None
        self.info_cache.similar_tracks_bean = self.bean

        """similar  songs"""
        similar_tracks = self.controls.lastfm_service.search_top_similar_tracks(self.bean.artist, self.bean.title)
        parent = FModel(_("Similar Tracks:") + " " + self.bean.title)
        update_parent_for_beans(similar_tracks, parent)
        self.tracks.populate_all([parent] + similar_tracks)

    def show_similar_artists(self):
        if self.info_cache.similar_artists_bean == self.bean:
            return None
        self.info_cache.similar_artists_bean = self.bean

        """similar  artists"""
        if self.bean.artist:
            similar_artists = self.controls.lastfm_service.search_top_similar_artist(self.bean.artist)
            parent = FModel(_("Similar Artists:") + " " + self.bean.artist)
            update_parent_for_beans(similar_artists, parent)
            self.artists.populate_all([parent] + similar_artists)

    def show_best_songs(self):
        if self.info_cache.best_songs_bean == self.bean:
            return None

        self.info_cache.best_songs_bean = self.bean

        best_songs = self.controls.lastfm_service.search_top_tracks(self.bean.artist)
        parent = FModel(_("Best Songs:") + " " + self.bean.artist)
        update_parent_for_beans(best_songs, parent)
        self.best_songs.populate_all([parent] + best_songs)

    @idle_task
    def set_lyrics(self, text, title):
        self.lyrics.set_text(text, title)
        self.controls.coverlyrics.lyrics.set_text(text, title)

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
