'''
Created on 25 Apr 2010

@author: Matik
'''
from __future__ import with_statement

import gtk
from gobject import TYPE_NONE, TYPE_PYOBJECT, TYPE_STRING #@UnresolvedImport

import thread

from foobnix.online.vk import Vkontakte
from foobnix.util import LOG
from foobnix.util.configuration import FConfiguration
import foobnix.online.integration.lastfm as lastfm
from foobnix.base import BaseController, SIGNAL_RUN_FIRST


try:
    vkontakte = Vkontakte(FConfiguration().vk_login, FConfiguration().vk_password)
except:
    vkontakte = None
    LOG.error("Vkontakte connection error")

class SearchPanel(BaseController):
    
    __gsignals__ = {
        'show_search_results': (SIGNAL_RUN_FIRST, TYPE_NONE, (TYPE_STRING, TYPE_PYOBJECT)),
        'starting_search': (SIGNAL_RUN_FIRST, TYPE_NONE, ()),
    }
    
    def __init__(self, gx_main):
        BaseController.__init__(self)
        self.search_routine = lastfm.search_top_tracks
        self.create_search_mode_buttons(gx_main)
        self.search_text = gx_main.get_widget("search_entry")
        self.search_text.connect("activate", self.on_search)    # GTK manual doesn't recommend to do this
        #self.search_text.connect("key-press-event", self.on_key_pressed)
        search_button = gx_main.get_widget("search_button")
        search_button.connect("clicked", self.on_search)
        self.lock = thread.allocate_lock()
        self.search_thread_id = None


    def on_key_pressed(self, w, event):
        if event.type == gtk.gdk.KEY_PRESS: #@UndefinedVariable
            #Enter pressed
            print "keyval", event.keyval, "keycode", event.hardware_keycode
            if event.hardware_keycode == 36:
                self.on_search()

    
    def get_search_query(self):
        query = self.search_text.get_text()
        if query and len(query.strip()) > 0:
            print query
            return query
        #Nothing found
        return None

    
    def create_search_mode_buttons(self, gx_main):
        mode_to_button_map = {lastfm.search_top_tracks    : 'top_songs_togglebutton',
                              lastfm.search_top_albums    : 'top_albums_togglebutton',
                              lastfm.search_top_similar   : 'top_similar_togglebutton',
                              vkontakte.find_song_urls    : 'all_search_togglebutton',
                              lastfm.search_tags_genre    : 'tags_togglebutton',
                              lastfm.unimplemented_search : 'tracks_togglebutton' }
        self.search_mode_buttons = {}
        for mode, name in mode_to_button_map.items():
            button = gx_main.get_widget(name)
            button.connect('toggled', self.on_search_mode_selected, mode)
            self.search_mode_buttons[mode] = button


    def on_search_mode_selected(self, clicked_button, selected_mode=None):
        # Look if the clicked button was the only button that was checked. If yes, then turn 
        # it back to checked - we don't allow all buttons to be unchecked at the same time
        if all( [not button.get_active() for button in self.search_mode_buttons.values()] ):
            clicked_button.set_active(True)

        # if the button should become unchecked, then do nothing
        if not clicked_button.get_active(): 
            return

        # so, the button becomes checked. Uncheck all other buttons
        for button in self.search_mode_buttons.values():
            if button != clicked_button:
                button.set_active(False)

        self.search_routine = selected_mode
        

    def capitilize_query(self, line):
        line = line.strip()
        result = ""
        for l in line.split():
            result += " " + l[0].upper() + l[1:]
        return result

    
    def on_search(self, *args):
        with self.lock:
            if self.search_thread_id:
                return None
    
            self.emit('starting_search')
            LOG.error('>>>>>>> search with ' + str(self.search_routine))
            query = self.get_search_query()
            if query:
                query = self.capitilize_query(u"" + query)
                self.search_thread_id = thread.start_new_thread(self.perform_search, (query,))
                #self.perform_search(query)

    
    def perform_search(self, query):
        beans = None
        try:
            if self.search_routine:
                beans = self.search_routine(query)
        except BaseException, ex:
            LOG.error('Error while search for %s: %s' % (query, ex))
        self.emit('show_search_results', query, beans)
        self.search_thread_id = None
