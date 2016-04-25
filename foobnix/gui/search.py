from gi.repository import Gtk
import thread
import logging

from foobnix.util.key_utils import is_key_enter
from foobnix.gui.model.signal import FControl
from foobnix.util.text_utils import capitalize_query
from foobnix.helpers.toggled import OneActiveToggledButton


class SearchControls(FControl, Gtk.Box):
    def __init__(self, controls):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        FControl.__init__(self, controls)
        self.controls = controls

        label = Gtk.Label.new(None)
        label.set_markup("<b>%s:</b>" % _("Search music online"))

        """default search function"""
        self.search_function = self.controls.search_top_tracks
        self.buttons = []

        self.pack_start(self.search_line(), False, False, 0)

        #self.pack_start(controls.search_progress, False, False, 0)

        self.show_all()
        """search on enter"""
        for button in self.buttons:
            button.connect("key-press-event", self.on_search_key_press)

        """only one button active"""
        OneActiveToggledButton(self.buttons)

    def set_search_function(self, search_function):
        logging.info("Set search function" + str(search_function))
        self.search_function = search_function

    def on_search(self, *w):
        thread.start_new_thread(self._on_search, ())
        #Otherwise you can't call authorization window,
        #it can be called only from not main loop

    def _on_search(self):
        def task():
            if self.get_query():
                if self.get_query().startswith("http://vk"):
                    self.controls.search_vk_page_tracks(self.get_query())
                else:
                    self.search_function(self.get_query())
        self.controls.net_wrapper.execute(task)

    def get_query(self):
        query = self.entry.get_text()
        return capitalize_query(query)

    def search_line(self):
        self.entry = Gtk.Entry()
        online_text = _("Online Music Search, Play, Download")

        self.entry.connect("key-press-event", self.on_search_key_press)

        self.entry.set_placeholder_text(online_text)

        combobox = self.combobox_creator()

        search_button = Gtk.Button.new_with_label(_("Search"))
        search_button.connect("clicked", self.on_search)

        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 0)
        searchLable = Gtk.Label.new(None)
        searchLable.set_markup("<b>%s</b>" % _("Online Search"))

        ##if Gtk.pygtk_version < (2, 22, 0):
        ##    hbox.pack_start(self.controls.search_progress, False, False)

        hbox.pack_start(combobox, False, False, 0)
        hbox.pack_start(self.entry, True, True, 0)
        hbox.pack_start(search_button, False, False, 0)
        hbox.show_all()

        return hbox

    def set_search_text(self, text):
        self.entry.set_text(text)

    def on_search_key_press(self, w, e):
        if is_key_enter(e):
            self.on_search()
            self.entry.grab_focus()

    def combobox_creator(self):
        list_func = []
        liststore = Gtk.ListStore(str)

        liststore.append([_("Tracks")])
        list_func.append(self.controls.search_top_tracks)

        liststore.append([_("Albums")])
        list_func.append(self.controls.search_top_albums)

        liststore.append([_("Similar")])
        list_func.append(self.controls.search_top_similar)

        liststore.append([_("Genre")])
        list_func.append(self.controls.search_top_tags)

        liststore.append([_("VKontakte")])
        list_func.append(self.controls.search_all_tracks)

        #liststore.append([_("Video")])
        #list_func.append(self.controls.search_all_videos)

        combobox = Gtk.ComboBox(model=liststore)
        cell = Gtk.CellRendererText()
        combobox.pack_start(cell, True)
        combobox.add_attribute(cell, 'text', 0)
        combobox.set_active(0)
        self.set_search_function(list_func[0])

        def on_changed(combobox):
            n = combobox.get_active()
            self.set_search_function(list_func[n])
            self.entry.grab_focus()

        combobox.connect("changed", on_changed)
        return combobox

    def show_menu(self, w, event, menu):
        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)
