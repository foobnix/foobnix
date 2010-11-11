'''
Created on Sep 22, 2010

@author: ivan
'''
import gtk
from foobnix.util import LOG, const
from foobnix.util.fc import FC
from foobnix.regui.model.signal import FControl
from foobnix.helpers.my_widgets import open_link_in_browser

class MenuWidget(FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        """TOP menu constructor"""

        top = TopMenu()
        """File"""
        file = top.append("File")
        file.add_image_item("Add File(s)", gtk.STOCK_OPEN, self.controls.on_add_files)
        file.add_image_item("Add Folder(s)", gtk.STOCK_OPEN, self.controls.on_add_folders)
        file.separator()
        file.add_image_item("Quit", gtk.STOCK_QUIT, self.controls.quit)


        """View"""
        view = top.append("View")
        self.view_music_tree = view.add_ckeck_item("Left Panel", FC().is_view_music_tree_panel)
        self.view_music_tree.connect("activate", lambda w: controls.set_visible_musictree_panel(w.get_active()))

        self.view_search_panel = view.add_ckeck_item("Search Panel")
        self.view_search_panel.connect("activate", lambda w: controls.set_visible_search_panel(w.get_active()))

        view.separator()

        view.separator()
        view.add_image_item("Equalizer", None, self.controls.eq.show)
        view.add_image_item("Download Manager", None, self.controls.dm.show)
        view.separator()
        view.add_image_item("Preferences", gtk.STOCK_PREFERENCES, self.controls.show_preferences)

        """Playback"""
        playback = top.append("Playback")

        def set_random(flag=True):            
            FC().is_order_random = flag
            LOG.debug("set random", flag)

        """Playback - Order"""
        order = playback.add_text_item("Order")
        self.playback_order_linear = order.add_radio_item("Linear", None, not FC().is_order_random)
        self.playback_order_linear.connect("activate", lambda w: set_random(False))
        
        self.playback_order_random = order.add_radio_item("Random", self.playback_order_linear, FC().is_order_random)
        self.playback_order_random.connect("activate", lambda w: set_random(True))
        
        #order.separator()
        #order.add_image_item("Shuffle", gtk.STOCK_UNDELETE)

        """Playback - Repeat"""
        repeat = playback.add_text_item("Repeat")
        self.lopping_all = repeat.add_radio_item("All", None, FC().repeat_state == const.REPEAT_ALL)
        self.lopping_single = repeat.add_radio_item("Single", self.lopping_all, FC().repeat_state == const.REPEAT_SINGLE)
        self.lopping_disable = repeat.add_radio_item("Disable", self.lopping_all, FC().repeat_state == const.REPEAT_NO)
        
        def repeat_all():
            FC().repeat_state = const.REPEAT_ALL
            LOG.debug("set repeat_all")
        
        def repeat_sigle():
            FC().repeat_state = const.REPEAT_SINGLE
            LOG.debug("set repeat_sigle")
        
        def repeat_no():
            FC().repeat_state = const.REPEAT_NO
            LOG.debug("set repeat_no")
            
        self.lopping_all.connect("activate", lambda *a:repeat_all())
        self.lopping_single.connect("activate", lambda *a:repeat_sigle())
        self.lopping_disable.connect("activate", lambda *a:repeat_no())

        """Playlist View"""
        #playlist = playback.add_text_item("Playlist")
        #self.playlist_plain = playlist.add_radio_item("Plain (normal style)", None, FC().playlist_type == const.PLAYLIST_PLAIN)
        #self.playlist_tree = playlist.add_radio_item("Tree (apollo style)", self.playlist_plain , FC().playlist_type == const.PLAYLIST_TREE)

        #self.playlist_plain.connect("activate", lambda w: w.get_active() and controls.set_playlist_plain())
        #self.playlist_tree.connect("activate", lambda w: w.get_active() and controls.set_playlist_tree())

        """Help"""
        help = top.append("Help")
        help.add_image_item("About", gtk.STOCK_ABOUT, self.controls.about.show_all)
        help.add_text_item("Project page", lambda * a:open_link_in_browser("http://www.foobnix.com"), None, False)
        help.add_image_item("Issue report", gtk.STOCK_DIALOG_WARNING, lambda * a:open_link_in_browser("http://code.google.com/p/foobnix/issues/list"))
        
        #help.add_image_item("Help", gtk.STOCK_HELP)

        top.decorate()
        self.widget = top.widget

        self.on_load()
    
    def on_load(self):
        self.view_music_tree.set_active(FC().is_view_music_tree_panel)
        self.view_search_panel.set_active(FC().is_view_search_panel)
        
    def on_save(self):
        FC().is_view_music_tree_panel = self.view_music_tree.get_active()
        FC().is_view_search_panel = self.view_search_panel.get_active()
        

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
        if func and param:
            item.connect("activate", lambda * a: func(param))
        elif func:
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

    def add_text_item(self, title, func=None, param=None, sub_menu=True):
        sub = gtk.MenuItem(title)
        sub.show()
        self.append(sub)
        
        if param and func:
            sub.connect("activate", lambda * a: func(param))
        elif func:
            sub.connect("activate", lambda * a: func())

        if sub_menu:
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
        label = gtk.Button()
        style = label.get_style()
        base = style.base[gtk.STATE_NORMAL]
        fg = style.fg[gtk.STATE_NORMAL]
        bg = style.bg[gtk.STATE_NORMAL]
        
        #fg =  gtk.gdk.color_parse("BLUE")
        #bg =  gtk.gdk.color_parse("RED")
        #base =  gtk.gdk.color_parse("GREEN")
        
        #self.menu_bar.modify_base(gtk.STATE_NORMAL, base)
        self.menu_bar.modify_fg(gtk.STATE_NORMAL, fg)
        self.menu_bar.modify_bg(gtk.STATE_NORMAL, bg)
        
        # making main menu look a bit better
        for item in self.menu_bar.get_children():
            current = item.get_children()[0]

            current.modify_fg(gtk.STATE_NORMAL, fg)
            current.modify_bg(gtk.STATE_NORMAL, bg)
            

    def append(self, title):
        menu = MyMenu()
        menu.show()

        file_item = gtk.MenuItem(title)
        file_item.show()

        file_item.set_submenu(menu)

        self.menu_bar.append(file_item)

        return menu


