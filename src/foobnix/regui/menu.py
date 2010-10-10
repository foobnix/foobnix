'''
Created on Sep 22, 2010

@author: ivan
'''
import gtk
from foobnix.util import LOG, const
import sys
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl

class MenuWidget(FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        """TOP menu constructor"""

        top = TopMenu()
        """File"""
        file = top.append("File")
        file.add_image_item("Add File(s)", gtk.STOCK_OPEN)
        file.add_image_item("Add Folder(s)", gtk.STOCK_OPEN)
        file.separator()
        file.add_image_item("Quit", gtk.STOCK_QUIT, self.controls.quit)


        """View"""
        view = top.append("View")
        self.view_music_tree = view.add_ckeck_item("Music Tree", FC().is_view_music_tree_panel)
        self.view_music_tree.connect("activate", lambda w: controls.set_visible_musictree_panel(w.get_active()))

        self.view_search_panel = view.add_ckeck_item("Search Panel", FC().is_view_info_panel)
        self.view_search_panel.connect("activate", lambda w: controls.set_visible_search_panel(w.get_active()))

        view.separator()
        #view.add_ckeck_item("Lyric Panel", FC().is_view_lyric_panel)
        self.view_info_panel = view.add_ckeck_item("Info Panel", FC().is_view_info_panel)
        self.view_info_panel.connect("activate", lambda w: controls.set_visible_info_panel(w.get_active()))


        view.separator()
        view.add_image_item("Equalizer", None, self.controls.eq.show)
        view.add_image_item("Download", None, self.controls.dm.show)
        view.separator()
        view.add_image_item("Preferences", gtk.STOCK_PREFERENCES, self.controls.show_preferences)

        """Playback"""
        playback = top.append("Playback")

        """Playback - Order"""
        order = playback.add_text_item("Order")
        self.playback_order_linear = order.add_radio_item("Linear", None, not FC().is_order_random)
        self.playback_order_random = order.add_radio_item("Random", self.playback_order_linear, FC().is_order_random)
        self.playback_order_random.connect("activate", lambda w: controls.set_playback_random(w.get_active()))
        order.separator()
        order.add_image_item("Shuffle", gtk.STOCK_UNDELETE)

        """Playback - Repeat"""
        repeat = playback.add_text_item("Repeat")
        self.lopping_all = repeat.add_radio_item("All", None, FC().lopping == const.LOPPING_LOOP_ALL)
        self.lopping_single = repeat.add_radio_item("Single", self.lopping_all, FC().lopping == const.LOPPING_SINGLE)
        self.lopping_disable = repeat.add_radio_item("Disable", self.lopping_all, FC().lopping == const.LOPPING_DONT_LOOP)
        self.lopping_all.connect("activate", lambda w: w.get_active() and controls.set_lopping_all())
        self.lopping_single.connect("activate", lambda w: w.get_active() and controls.set_lopping_single())
        self.lopping_disable.connect("activate", lambda w: w.get_active() and controls.set_lopping_disable())

        """Playlist View"""
        playlist = playback.add_text_item("Playlist")
        self.playlist_plain = playlist.add_radio_item("Plain (normal style)", None, FC().playlist_type == const.PLAYLIST_PLAIN)
        self.playlist_tree = playlist.add_radio_item("Tree (apollo style)", self.playlist_plain , FC().playlist_type == const.PLAYLIST_TREE)

        self.playlist_plain.connect("activate", lambda w: w.get_active() and controls.set_playlist_plain())
        self.playlist_tree.connect("activate", lambda w: w.get_active() and controls.set_playlist_tree())

        """Help"""
        help = top.append("Help")
        help.add_image_item("About", gtk.STOCK_ABOUT,self.controls.about.show_all)
        help.add_image_item("Help", gtk.STOCK_HELP)

        top.decorate()
        self.widget = top.widget

        self.on_load()

    def on_load(self):
        self.view_music_tree.set_active(FC().is_view_music_tree_panel)
        self.view_search_panel.set_active(FC().is_view_search_panel)
        self.view_info_panel.set_active(FC().is_view_info_panel)

    def on_save(self):
        FC().is_view_music_tree_panel = self.view_music_tree.get_active()
        FC().is_view_search_panel = self.view_search_panel.get_active()
        FC().is_view_info_panel = self.view_info_panel.get_active()

class MyMenu(gtk.Menu):
    """My custom menu class for helping buildings"""
    def __init__(self):
        gtk.Menu.__init__(self)

    def add_image_item(self, title, gtk_stock, func=None, param=None):
        item = gtk.ImageMenuItem(title)
        item.show()
        if gtk_stock:
            img = gtk.image_new_from_stock(gtk_stock, gtk.ICON_SIZE_MENU)
            item.set_image(img)

        LOG.debug("Menu-Image-Activate", title, gtk_stock, func, param)
        if param:
            item.connect("activate", lambda * a: func(param))
        else:
            item.connect("activate", lambda * a: func())

        self.append(item)

    def separator(self):
        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.append(separator)

    def add_ckeck_item(self, title, active=False, func=None, param=None):
        check = gtk.CheckMenuItem(title)

        if param and func:
            check.connect("activate", lambda * a: func(param))
        elif func:
            check.connect("activate", lambda * a: func())

        check.show()
        check.set_active(active)
        self.append(check)
        return check

    def add_radio_item(self, title, group, active):
        check = gtk.RadioMenuItem(group, title)
        check.show()
        check.set_active(active)
        self.append(check)
        return check

    def add_text_item(self, title):
        sub = gtk.MenuItem(title)
        sub.show()
        self.append(sub)

        menu = MyMenu()
        menu.show()
        sub.set_submenu(menu)

        return menu

"""My top menu bar helper"""
class TopMenu():
    def __init__(self):
        rc_st = '''
            style "menubar-style" {
                GtkMenuBar::shadow_type = none
                GtkMenuBar::internal-padding = 0
                }
            class "GtkMenuBar" style "menubar-style"
        '''
        gtk.rc_parse_string(rc_st)

        self.menu_bar = gtk.MenuBar()
        self.menu_bar.show()

        self.widget = self.menu_bar

    def decorate(self):
        label = gtk.Label()
        style = label.get_style()
        background_color = style.bg[gtk.STATE_NORMAL]
        text_color = style.fg[gtk.STATE_NORMAL]

        self.menu_bar.modify_bg(gtk.STATE_NORMAL, background_color)

        # making main menu look a bit better
        for item in self.menu_bar.get_children():
            current = item.get_children()[0]
            current.modify_fg(gtk.STATE_NORMAL, text_color)

    def append(self, title):
        menu = MyMenu()
        menu.show()

        file_item = gtk.MenuItem(title)
        file_item.show()

        file_item.set_submenu(menu)

        self.menu_bar.append(file_item)

        return menu


