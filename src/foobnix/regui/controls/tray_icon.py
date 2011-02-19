#-*- coding: utf-8 -*-
'''
Created on 29 сент. 2010

@author: ivan
'''

import gtk

from foobnix.util.fc import FC
from foobnix.util.mouse_utils import is_middle_click
from foobnix.regui.state import LoadSave
from foobnix.regui.model.signal import FControl
from foobnix.helpers.image import ImageBase
from foobnix.regui.model import FModel
from foobnix.helpers.pref_widgets import VBoxDecorator
from foobnix.util.text_utils import split_string
import logging
from foobnix.regui.controls.playback import PlaybackControls
from foobnix.helpers.my_widgets import ImageButton
from foobnix.util.const import ICON_FOOBNIX

 
class PopupWindowMenu(gtk.Window, FControl):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.Window. __init__(self, gtk.WINDOW_POPUP)

        self.set_position(gtk.WIN_POS_MOUSE)

        self.connect("leave-notify-event", self.on_leave_window)

        vbox = gtk.VBox(False, 0)

        
        playcontrols = PlaybackControls(controls)
        playcontrols.pack_start(ImageButton(gtk.STOCK_QUIT, controls.quit, _("Exit")))
        playcontrols.pack_start(ImageButton(gtk.STOCK_OK, self.hide, _("Close Popup")))

        self.poopup_text = gtk.Label("Foobnix")
        self.poopup_text.set_line_wrap(True)

        vbox.pack_start(playcontrols, False, False)
        vbox.pack_start(self.poopup_text, False, False)
        self.add(vbox)
        self.show_all()
        self.hide()
        
    def set_text(self, text):
        self.poopup_text.set_text(text[:40])

    def on_leave_window(self, w, event):
        max_x, max_y = w.size_request()
        x, y = event.x, event.y
        if 0 < x < max_x and 0 < y < max_y:
            return True
        self.hide()


class TrayIconControls(gtk.StatusIcon, ImageBase, FControl, LoadSave):
    def __init__(self, controls):
        FControl.__init__(self, controls)
        gtk.StatusIcon.__init__(self)
        self.hide()
        
        ImageBase.__init__(self, ICON_FOOBNIX, 150)
        
        self.popup_menu = PopupWindowMenu(self.controls)
        
        self.connect("activate", self.on_activate)
        self.connect("popup-menu", self.on_popup_menu)

        try:
            self.set_has_tooltip(True)        
            self.tooltip = gtk.Tooltip()
            self.set_tooltip("Foobnix music player")
            self.connect("query-tooltip", self.on_query_tooltip)
            self.connect("button-press-event", self.on_button_press)
            self.connect("scroll-event", self.controls.volume.on_scroll_event)
        except Exception, e:
            logging.warn("On debian it doesn't work" + str(e))
        
        self.current_bean = FModel().add_artist("Artist").add_title("Title")
        self.tooltip_image = ImageBase(ICON_FOOBNIX, 75)
    
    def on_save(self):
        pass
        
  
    def on_load(self):
        print "load"
        print FC().static_icon_entry
        if FC().show_tray_icon:
            if FC().static_tray_icon:
                self.set_from_resource(FC().static_icon_entry)               
            self.show()
        else:
            self.hide()
                
    def update_info_from(self, bean):
        self.current_bean = bean
        if bean.artist:
            artist = bean.artist
            self.tooltip_image.size = 150
        else: 
            artist = 'Unknown artist'
            self.tooltip_image.size = 75
            self.tooltip_image.resource = ICON_FOOBNIX
        self.tooltip_image.update_info_from(bean)
        
        if bean.title: 
            title = bean.title
        else: 
            title = bean.text
        if FC().change_tray_icon:
            super(TrayIconControls, self).update_info_from(bean)

        if FC().notifier:
            try:
                import pynotify
                if not pynotify.init('org.mpris.foobnix'):
                    logging.warning("Can't initialize pynotify")
                    return
                notification = pynotify.Notification("<b><big>Foobnix</big></b>", "<b><i> " + artist + "\n\n " + title + "</i></b>")
                notification.set_urgency(pynotify.URGENCY_LOW)
                notification.set_timeout(FC().notify_time)
                notification.set_icon_from_pixbuf(self.tooltip_image.get_pixbuf())
                notification.show()
            except:
                logging.warn("Pynotify not found in your system")

    def on_query_tooltip(self, widget, x, y, keyboard_tip, tooltip):
        artist = "Artist"
        title = "Title"
        if self.current_bean:
            if self.current_bean.artist and self.current_bean.title:
                artist = self.current_bean.artist
                #artist = string.join(["&amp;" if x == '&' else x for x in artist], '')
                artist = artist.replace('&', '&amp;')
                title = self.current_bean.title
            else:
                artist = "Unknown artist"
                title = self.current_bean.text
        
        max_str_len = 40
        if len(title) > max_str_len:
            title = split_string(title, max_str_len)
        
        alabel = gtk.Label()
        alabel.set_markup("<b>%s</b>" % artist)
        hbox1 = gtk.HBox()
        hbox1.pack_start(alabel, False, False)
        hbox2 = gtk.HBox()
        hbox2.pack_start(gtk.Label(title), False, False)        
        vbox = VBoxDecorator(gtk.Label(), hbox1, gtk.Label(), hbox2)        
        if self.tooltip_image.size == 150:
            alignment = gtk.Alignment(0, 0.4)
        else:
            alignment = gtk.Alignment()
        alignment.set_padding(padding_top=0, padding_bottom=0, padding_left=10, padding_right=10)
        alignment.add(vbox)
        tooltip.set_icon(self.tooltip_image.get_pixbuf())
        tooltip.set_custom(alignment)
        return True
    
    def on_activate(self, *a):
        self.controls.windows_visibility()

    def on_button_press(self, w, e):
        if is_middle_click(e):            
            self.controls.play_pause()

    def hide(self):
        self.set_visible(False)

    def show(self):
        self.set_visible(True)

    def show_window(self, *a):
        self.popup_menu.reshow_with_initial_size()
        self.popup_menu.show()

    def hide_window(self, *a):
        self.popup_menu.hide()

    def on_popup_menu(self, *a):
        self.show_window()

    def set_text(self, text):
        self.popup_menu.set_text(text)
        self.set_tooltip(text)
       
