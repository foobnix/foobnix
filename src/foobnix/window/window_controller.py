'''
Created on Mar 13, 2010

@author: ivan
'''
import gtk
from foobnix.util.configuration import VERSION
from foobnix.base import BaseController
from foobnix.base import SIGNAL_RUN_FIRST, TYPE_NONE

class WindowController(BaseController):

    __gsignals__ = {
        'exit' : (SIGNAL_RUN_FIRST, TYPE_NONE, ()),
        'show_preferences' : (SIGNAL_RUN_FIRST, TYPE_NONE, ()),
    }

    def __init__(self, gx_main_window, gx_about):
        BaseController.__init__(self)
        self.decorate(gx_main_window)

        popup_signals = {
                "on_gtk-preferences_activate": lambda * a: self.emit('show_preferences'),
                "on_file_quit_activate": lambda * a: self.emit('exit'),
                "on_menu_about_activate": self.show_about_window
        }
        gx_main_window.signal_autoconnect(popup_signals)

        self.main_window = gx_main_window.get_widget("foobnixWindow")
        self.main_window.connect("delete-event", self.hide)
        self.main_window.set_title("Foobnix " + VERSION)
        self.main_window.maximize()

        self.about_window = gx_about.get_widget("aboutdialog")
        self.about_window.connect("delete-event", self.hide_about_window)

    def on_song_started(self, sender, song):
        self.main_window.set_title(song.getTitleDescription())

    def show_about_window(self, *args):
        self.about_window.show()

    def hide_about_window(self, *args):
        self.about_window.hide()
        return True

    def show(self):
        self.main_window.show()

    def hide(self, *args):
        self.main_window.hide()
        return True

    def toggle_visibility(self, *a):
        visible = self.main_window.get_property('visible')
        self.main_window.set_property('visible', not visible)

    def decorate(self, gx):
        rc_st = '''
            style "menubar-style" { 
                GtkMenuBar::shadow_type = none
                GtkMenuBar::internal-padding = 0
                }
            class "GtkMenuBar" style "menubar-style"
        '''
        gtk.rc_parse_string(rc_st)

        style = gx.get_widget("label6").get_style()
        background_color = style.bg[gtk.STATE_NORMAL]
        text_color = style.fg[gtk.STATE_NORMAL]
        menu_bar = gx.get_widget("menubar3")
        menu_bar.modify_bg(gtk.STATE_NORMAL, background_color)

        # making main menu look a bit better
        for item in menu_bar.get_children():
            current = item.get_children()[0]
            current.modify_fg(gtk.STATE_NORMAL, text_color)
